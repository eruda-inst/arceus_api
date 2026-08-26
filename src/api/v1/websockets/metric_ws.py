from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, db

metric_ws_router = APIRouter(prefix="/metricas", tags=["Métricas WS"])


Action = Literal["enroll", "unenroll"]

MetricNames = Literal[
    "erros",
    "sucessos",
    "tempo_resposta",
    "top_clientes",
    "total_atendimentos",
    "total_requisicoes",
    "top_dias_mes",
    "top_dias_semana",
    "top_endpoints",
    "top_endpoints_mais_lentos",
    "top_horas",
    "top_metodos_http",
    "top_piores_endpoints",
    "top_setores",
    "top_status_codes",
]


class MessageInSchema(BaseModel):
    action: Action | None = Field(
        default="enroll", description="Descrição em português aqui"
    )
    metric_names: list[MetricNames] | Literal["all"] = Field(
        description="Descrição em português aqui"
    )


class ConnectionManager:
    """
    Gerencia as conexões WebSocket ativas, organizando-as por tipo de métrica.
    Permite inscrever/desinscrever um cliente em uma ou várias métricas,
    e enviar mensagens (broadcast) para todos os clientes inscritos em determinadas métricas
    """

    def __init__(self) -> None:
        # Inicializa um dicionário com uma lista vazia para cada nome de métrica
        self.active_connections: dict[MetricNames, list[WebSocket]] = {
            "erros": [],
            "sucessos": [],
            "tempo_resposta": [],
            "top_clientes": [],
            "total_atendimentos": [],
            "total_requisicoes": [],
            "top_dias_mes": [],
            "top_dias_semana": [],
            "top_endpoints": [],
            "top_endpoints_mais_lentos": [],
            "top_horas": [],
            "top_metodos_http": [],
            "top_piores_endpoints": [],
            "top_setores": [],
            "top_status_codes": [],
        }

    def enroll(
        self, ws: WebSocket, metric_names: list[MetricNames] | Literal["all"]
    ) -> None:
        """
        Inscreve um cliente WebSocket em uma ou várias métricas.
        Se metric_names for "all", inscreve em todas as métricas disponíveis
        """
        if metric_names == "all":
            for name in self.active_connections:
                if ws not in self.active_connections[name]:
                    self.active_connections[name].append(ws)
        else:
            for name in metric_names:
                if (
                    name in self.active_connections
                    and ws not in self.active_connections[name]
                ):
                    self.active_connections[name].append(ws)

    def unenroll(
        self, ws: WebSocket, metric_names: list[MetricNames] | Literal["all"]
    ) -> None:
        """
        Desinscreve um cliente WebSocket de uma ou várias métricas.
        Se metric_names for "all", desinscreve de todas as métricas
        """
        if metric_names == "all":
            for name in self.active_connections:
                if ws in self.active_connections[name]:
                    self.active_connections[name].remove(ws)
        else:
            for name in metric_names:
                if (
                    name in self.active_connections
                    and ws in self.active_connections[name]
                ):
                    self.active_connections[name].remove(ws)

    async def broadcast(
        self,
        metric_names: list[MetricNames] | Literal["all"],
        message: dict[str, Any],
    ) -> None:
        """
        Envia uma mensagem (formato JSON) para todos os clientes inscritos
        nas métricas especificadas. Se metric_names for "all", envia para todos
        """
        if metric_names == "all":
            for name in self.active_connections:
                for active_connection in self.active_connections[name]:
                    await active_connection.send_json(message)
        else:
            for name in metric_names:
                if name in self.active_connections:
                    for active_connection in self.active_connections[name]:
                        await active_connection.send_json(message)


manager = ConnectionManager()


async def unicast_metrics(
    db: AsyncSession, ws: WebSocket, metric_names: list[MetricNames] | Literal["all"]
) -> None:
    """
    Busca os dados atualizados das métricas solicitadas e os envia
    unicamente para o WebSocket especificado (não faz broadcast).
    A mensagem final é um dicionário cujas chaves são os nomes das métricas
    e os valores são os resultados obtidos via CRUD
    """
    message = {}

    # Para cada métrica, verifica se está na lista ou se foi solicitado "all",
    # então consulta o respectivo método do CRUD e adiciona ao dicionário
    if "erros" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_error_stats(db=db)
        message["erros"] = res.model_dump()
    if "sucessos" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_success_stats(db=db)
        message["sucessos"] = res.model_dump()
    if "tempo_resposta" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_res_time(db=db)
        message["tempo_resposta"] = res.model_dump()
    if "top_clientes" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_top_clients(db=db)
        message["top_clientes"] = res.model_dump()
    if "top_dias_mes" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_top_month_days(db=db)
        message["top_dias_mes"] = res.model_dump()
    if "top_dias_semana" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_top_weekdays(db=db)
        message["top_dias_semana"] = res.model_dump()
    if "top_endpoints" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_top_endpoints(db=db)
        message["top_endpoints"] = res.model_dump()
    if "top_endpoints_mais_lentos" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_top_slowest_endpoints(db=db)
        message["top_endpoints_mais_lentos"] = res.model_dump()
    if "top_horas" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_top_hours(db=db)
        message["top_horas"] = res.model_dump()
    if "top_metodos_http" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_top_http_methods(db=db)
        message["top_metodos_http"] = res.model_dump()
    if "top_piores_endpoints" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_worst_endpoints(db=db)
        message["top_piores_endpoints"] = res.model_dump()
    if "top_setores" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_top_departments(db=db)
        message["top_setores"] = res.model_dump()
    if "top_status_codes" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_top_status_codes(db=db)
        message["top_status_codes"] = res.model_dump()
    if "total_atendimentos" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_total_services(db=db)
        message["total_atendimentos"] = res.model_dump()
    if "total_requisicoes" in metric_names or metric_names == "all":
        res = await cruds.MetricCrud.get_total_reqs(db=db)
        message["total_requisicoes"] = res.model_dump()

    await ws.send_json(message)


@metric_ws_router.websocket(path="/")
async def get_metric(
    db: Annotated[AsyncSession, Depends(db.get_db)], ws: WebSocket
) -> None:
    """
    Endpoint WebSocket para receber inscrições/desinscrições em métricas
    e retornar os dados atualizados.

    Fluxo esperado:
    1. O cliente conecta e deve enviar uma primeira mensagem JSON com
       `action` (opcional, padrão "enroll") e `metric_names` (lista ou "all").
    2. O servidor aceita a conexão, processa a inscrição inicial e envia
       os dados atuais das métricas solicitadas.
    3. Em seguida, fica em loop aguardando novas mensagens do cliente.
       Cada nova mensagem pode conter `action` ("enroll" ou "unenroll") e
       `metric_names` para alterar a inscrição.
    4. Após cada ação, o servidor reenvia os dados atualizados para o cliente.
    5. Em caso de erro de validação, notifica o cliente e continua o loop.
    6. Em caso de desconexão, remove o cliente de todas as listas.
    """
    await ws.accept()

    try:
        # Mensagem inicial fora do loop
        raw = await ws.receive_json()
        initial_message = MessageInSchema(**raw)
        manager.enroll(ws=ws, metric_names=initial_message.metric_names)
        # O cliente recebe apenas dados atualizados do que ele pedir, o middleware
        # dá conta de atualizações subsequentes contínuas
        await unicast_metrics(db=db, ws=ws, metric_names=initial_message.metric_names)
    except ValidationError as e:
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
        manager.unenroll(ws=ws, metric_names="all")
        return

    # Loop principal para receber mensagens subsequentes
    while True:
        try:
            raw = await ws.receive_json()
            message = MessageInSchema(**raw)

            if message.action == "enroll":
                manager.enroll(ws=ws, metric_names=message.metric_names)
            else:  # "unenroll"
                manager.unenroll(ws=ws, metric_names=message.metric_names)

            # O cliente recebe apenas dados atualizados do que ele pedir, o middleware
            # dá conta de atualizações subsequentes contínuas
            await unicast_metrics(db=db, ws=ws, metric_names=message.metric_names)
        except ValidationError as e:
            # Erro de validação: notifica o cliente e continua o loop
            await ws.send_json(
                {
                    "type": "error",
                    "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
                    "detail": e,
                }
            )
        except WebSocketDisconnect:
            # Desconexão detectada: limpa as listas e encerra o loop
            manager.unenroll(ws=ws, metric_names="all")
            break
