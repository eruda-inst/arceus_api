from dataclasses import dataclass
from datetime import date, time
from typing import Annotated, Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field, PositiveInt, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, db, schemas

# Roteador para WebSockets de logs, prefixo "/logs"
log_ws_router = APIRouter(prefix="/logs", tags=["Logs WS"])


class ParamsInSchema(BaseModel):
    """
    Esquema de parâmetros recebidos via JSON do cliente WebSocket.
    Contém campos de paginação e filtros para a consulta de logs.
    Todos os campos são opcionais; se não fornecidos, assumem valores padrão.
    """

    # Paginação
    pagina: PositiveInt | None = Field(default=1, ge=1, description="Número da página")
    itens_por_pagina: PositiveInt | None = Field(
        default=10, ge=1, description="Itens por página"
    )
    # Filtros (parciais ou intervalares)
    metodo: str | None = Field(
        default=None, description="Filtro parcial por método HTTP"
    )
    endpoint: str | None = Field(
        default=None, description="Filtro parcial por endpoint"
    )
    codigo: PositiveInt | None = Field(
        default=None, ge=1, description="Filtro parcial por código de status HTTP"
    )
    data_inicio: str | None = Field(
        default=None, description="Filtro intervalal por data de início"
    )
    data_fim: str | None = Field(
        default=None, description="Filtro intervalal por data de fim"
    )
    hora_inicio: str | None = Field(
        default=None, description="Filtro intervalal por hora de início"
    )
    hora_fim: str | None = Field(
        default=None, description="Filtro intervalal por hora de fim"
    )
    protocolo: str | None = Field(
        default=None, description="Filtro parcial por protocolo de atendimento"
    )
    setor: str | None = Field(default=None, description="Filtro parcial por setor")
    nome_cliente: str | None = Field(
        default=None, description="Filtro parcial por nome do cliente"
    )


@dataclass
class Connection:
    """
    Representa uma conexão WebSocket ativa com seus parâmetros de filtro/paginação.
    Usada para armazenar o estado de cada cliente conectado.
    """

    socket: WebSocket
    params: ParamsInSchema


class ConnectionManager:
    """
    Gerencia as conexões WebSocket ativas para logs.
    Cada conexão possui um conjunto de parâmetros (filtros e paginação) que são
    usados para personalizar os dados enviados para aquele cliente específico.
    """

    def __init__(self) -> None:
        # Lista de todas as conexões ativas
        self.active_connections: list[Connection] = []

    def connect(self, ws: WebSocket, params: ParamsInSchema) -> None:
        """
        Adiciona uma nova conexão à lista de ativas, com os parâmetros fornecidos.
        Evita duplicatas verificando se a instância já existe.
        """
        instance = Connection(socket=ws, params=params)

        if instance not in self.active_connections:
            self.active_connections.append(instance)

    def disconnect(self, ws: WebSocket) -> None:
        """
        Remove uma conexão da lista de ativas, identificada pelo WebSocket.
        """
        for active_connection in self.active_connections:
            if active_connection.socket == ws:
                self.active_connections.remove(active_connection)
                break

    def change_params(self, ws: WebSocket, params: ParamsInSchema) -> None:
        """
        Atualiza os parâmetros de uma conexão existente, identificada pelo WebSocket.
        Usado quando o cliente envia uma nova mensagem com novos filtros/paginação.
        """
        for active_connection in self.active_connections:
            if active_connection.socket is ws:
                active_connection.params = params
                break

    async def unicast(self, db: AsyncSession, ws: WebSocket) -> None:
        """
        Envia os dados de logs filtrados e paginados exclusivamente para o WebSocket
        especificado (unicast). A consulta é feita diretamente no banco de dados
        usando os parâmetros armazenados para aquela conexão.

        Args:
            db: Sessão assíncrona do banco de dados.
            ws: WebSocket do cliente destino.
        """
        # Percorre as conexões ativas para encontrar a correspondente ao WebSocket
        for a_c in self.active_connections:
            socket, params = a_c.socket, a_c.params

            if socket == ws:
                # Obtém os valores de página e itens por página (com fallback para padrões)
                pagina = params.pagina or 1
                itens_por_pagina = params.itens_por_pagina or 10

                # Chama o CRUD para buscar os logs com todos os filtros aplicados
                total_items, logs = await cruds.LogCrud.get_all(
                    db=db,
                    page=pagina,
                    items_per_page=itens_por_pagina,
                    metodo=params.metodo,
                    endpoint=params.endpoint,
                    codigo=params.codigo,
                    data_inicio=params.data_inicio,
                    data_fim=params.data_fim,
                    hora_inicio=params.hora_inicio,
                    hora_fim=params.hora_fim,
                    protocolo=params.protocolo,
                    setor=params.setor,
                    nome_cliente=params.nome_cliente,
                )

                # Monta a resposta no formato esperado (lista + metadados de paginação)
                res = schemas.ListOutSchema[schemas.LogOutSchema](
                    data=[schemas.LogOutSchema.model_validate(log) for log in logs],
                    meta=schemas.MetaOutSchema(
                        pagina_atual=pagina,
                        itens_por_pagina=itens_por_pagina,
                        total_itens=total_items,
                    ),
                )

                # Envia a resposta JSON para o cliente
                await socket.send_json(res.model_dump(mode="json"))
                break  # Encontrou e enviou, sai do loop

    async def broadcast(self) -> None:
        """
        Envia em broadcast os logs mais recentes para TODOS os clientes conectados,
        aplicando os filtros individuais de cada um.

        Este método é chamado periodicamente (por exemplo, por um agendador) para
        atualizar todos os clientes com os dados mais recentes. Ele consulta todos
        os logs do banco de dados uma única vez e depois filtra em memória conforme
        os parâmetros de cada conexão, para otimizar o desempenho.
        """
        # Abre uma sessão assíncrona para consultar todos os logs
        async with db.AsyncSessionLocal() as session:
            # Busca todos os logs (sem paginação) e converte para dicionários
            _, all_logs = await cruds.LogCrud.get_all(db=session)
            all_dicts: list[dict[str, Any]] = [log.to_dict() for log in all_logs]

            # Para cada conexão ativa, aplica os filtros específicos e envia a página solicitada
            for a_c in self.active_connections:
                params = a_c.params
                # Começa com a lista completa de todos os logs
                filtered = all_dicts[:]

                # Aplica filtros parciais (case-insensitive) conforme os parâmetros
                if params.metodo:
                    search = params.metodo.lower()
                    filtered = [d for d in filtered if search in d["metodo"].lower()]
                if params.endpoint:
                    search = params.endpoint.lower()
                    filtered = [d for d in filtered if search in d["endpoint"].lower()]
                if params.codigo:
                    filtered = [d for d in filtered if d["codigo"] == params.codigo]
                if params.protocolo and params.protocolo.strip():
                    search = params.protocolo.lower()
                    filtered = [
                        d
                        for d in filtered
                        if d.get("protocolo") and search in d["protocolo"].lower()
                    ]
                if params.setor:
                    search = params.setor.lower()
                    filtered = [d for d in filtered if search in d["setor"].lower()]
                if params.nome_cliente and params.nome_cliente.strip():
                    search = params.nome_cliente.lower()
                    filtered = [
                        d
                        for d in filtered
                        if d.get("nome_cliente") and search in d["nome_cliente"].lower()
                    ]

                # Filtros intervalares por data e hora
                if params.data_inicio:
                    start_date = date.fromisoformat(params.data_inicio)
                    filtered = [
                        d for d in filtered if d["criado_em"].date() >= start_date
                    ]
                if params.data_fim:
                    end_date = date.fromisoformat(params.data_fim)
                    filtered = [
                        d for d in filtered if d["criado_em"].date() <= end_date
                    ]
                if params.hora_inicio:
                    start_time = time.fromisoformat(params.hora_inicio)
                    filtered = [
                        d for d in filtered if d["criado_em"].time() >= start_time
                    ]
                if params.hora_fim:
                    end_time = time.fromisoformat(params.hora_fim)
                    filtered = [
                        d for d in filtered if d["criado_em"].time() <= end_time
                    ]

                # Aplica paginação sobre a lista filtrada
                page = params.pagina or 1
                items_per_page = params.itens_por_pagina or 10
                total_items = len(filtered)
                start = (page - 1) * items_per_page
                end = start + items_per_page
                paginated_dicts = filtered[start:end]

                # Constrói a resposta com os dados paginados e metadados
                res = schemas.ListOutSchema(
                    data=[
                        schemas.LogOutSchema.model_validate(d).model_dump()
                        for d in paginated_dicts
                    ],
                    meta=schemas.MetaOutSchema(
                        pagina_atual=page,
                        itens_por_pagina=items_per_page,
                        total_itens=total_items,
                    ),
                )

                # Envia a resposta para o cliente específico
                await a_c.socket.send_json(res.model_dump(mode="json"))


# Instância única do gerenciador de conexões para logs
log_manager = ConnectionManager()


@log_ws_router.websocket(path="/")
async def get_logs(
    db: Annotated[AsyncSession, Depends(db.get_db)], ws: WebSocket
) -> None:
    """
    Endpoint WebSocket para receber logs com filtros e paginação em tempo real.

    Fluxo:
    1. Aceita a conexão WebSocket.
    2. Aguarda a primeira mensagem JSON contendo os parâmetros iniciais (filtros/página).
    3. Registra a conexão com esses parâmetros e envia imediatamente os dados correspondentes.
    4. Entra em loop aguardando novas mensagens do cliente:
       - Cada nova mensagem deve conter novos parâmetros (ou os mesmos).
       - Atualiza os parâmetros da conexão e reenvia os dados atualizados.
       - Em caso de erro de validação, envia uma mensagem de erro e continua o loop.
    5. Em caso de desconexão, remove a conexão da lista de ativas.
    """
    await ws.accept()

    try:
        # Recebe a mensagem inicial com os parâmetros
        raw = await ws.receive_json()
        initial_params = ParamsInSchema(**raw)
        # Conecta e guarda os parâmetros
        log_manager.connect(ws=ws, params=initial_params)
        # Envia os dados correspondentes para este cliente
        await log_manager.unicast(db=db, ws=ws)
    except ValidationError as e:
        # Se a mensagem inicial for inválida, notifica o erro e fecha a conexão
        await ws.send_json(
            {
                "type": "error",
                "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
                "detail": e,
            }
        )
        await ws.close()
        return
    except WebSocketDisconnect:
        # Cliente desconectou antes de enviar a mensagem inicial
        log_manager.disconnect(ws=ws)
        return

    # Loop principal para mensagens subsequentes
    while True:
        try:
            # Aguarda nova mensagem do cliente
            raw = await ws.receive_json()
            # Valida os parâmetros
            params = ParamsInSchema(**raw)
            # Atualiza os parâmetros da conexão
            log_manager.change_params(ws=ws, params=params)
            # Reenvia os dados com os novos parâmetros
            await log_manager.unicast(db=db, ws=ws)
        except ValidationError as e:
            # Erro de validação: notifica o cliente, mas mantém a conexão aberta
            await ws.send_json(
                {
                    "type": "error",
                    "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
                    "detail": e,
                }
            )
        except WebSocketDisconnect:
            # Desconexão: remove a conexão e encerra o loop
            log_manager.disconnect(ws=ws)
            break
