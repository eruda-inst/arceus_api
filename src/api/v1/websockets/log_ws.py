from dataclasses import dataclass
from datetime import date, time
from typing import Annotated, Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field, PositiveInt, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, db, models, schemas

log_ws_router = APIRouter(prefix="/logs", tags=["Logs WS"])


class ParamsInSchema(BaseModel):
    # Paginação
    pagina: PositiveInt | None = Field(default=1, ge=1, description="Número da página")
    itens_por_pagina: PositiveInt | None = Field(
        default=10, ge=1, description="Itens por página"
    )
    # Filtros
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
    socket: WebSocket
    params: ParamsInSchema


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[Connection] = []

    def connect(self, ws: WebSocket, params: ParamsInSchema) -> None:
        instance = Connection(socket=ws, params=params)

        if instance not in self.active_connections:
            self.active_connections.append(instance)

    def disconnect(self, ws: WebSocket) -> None:
        for active_connection in self.active_connections:
            if active_connection.socket == ws:
                self.active_connections.remove(active_connection)
                break

    def change_params(self, ws: WebSocket, params: ParamsInSchema) -> None:
        for active_connection in self.active_connections:
            if active_connection.socket is ws:
                active_connection.params = params
                break

    async def unicast(self, db: AsyncSession, ws: WebSocket) -> None:
        for a_c in self.active_connections:
            socket, params = a_c.socket, a_c.params

            if socket == ws:
                pagina = params.pagina or 1
                itens_por_pagina = params.itens_por_pagina or 10

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

                res = schemas.ListOutSchema[schemas.LogOutSchema](
                    data=[schemas.LogOutSchema.model_validate(log) for log in logs],
                    meta=schemas.MetaOutSchema(
                        pagina_atual=pagina,
                        itens_por_pagina=itens_por_pagina,
                        total_itens=total_items,
                    ),
                )

                await socket.send_json(res.model_dump(mode="json"))
                break

    async def broadcast(self) -> None:
        async with db.AsyncSessionLocal() as session:
            stmt = select(models.LogModel).order_by(models.LogModel.id.desc())
            result = await session.execute(stmt)
            all_logs = result.scalars().all()

            all_dicts: list[dict[str, Any]] = [log.to_dict() for log in all_logs]

            for a_c in self.active_connections:
                params = a_c.params
                filtered = all_dicts[:]

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

                page = params.pagina or 1
                items_per_page = params.itens_por_pagina or 10
                total_items = len(filtered)
                start = (page - 1) * items_per_page
                end = start + items_per_page
                paginated_dicts = filtered[start:end]

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

                await a_c.socket.send_json(res.model_dump())


log_manager = ConnectionManager()


@log_ws_router.websocket(path="/")
async def get_logs(
    db: Annotated[AsyncSession, Depends(db.get_db)], ws: WebSocket
) -> None:
    await ws.accept()

    try:
        raw = await ws.receive_json()
        initial_params = ParamsInSchema(**raw)
        log_manager.connect(ws=ws, params=initial_params)
        await log_manager.unicast(db=db, ws=ws)
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
        log_manager.disconnect(ws=ws)
        return

    while True:
        try:
            raw = await ws.receive_json()
            params = ParamsInSchema(**raw)
            log_manager.change_params(ws=ws, params=params)
            await log_manager.unicast(db=db, ws=ws)
        except ValidationError as e:
            await ws.send_json(
                {
                    "type": "error",
                    "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
                    "detail": e,
                }
            )
        except WebSocketDisconnect:
            log_manager.disconnect(ws=ws)
            break
