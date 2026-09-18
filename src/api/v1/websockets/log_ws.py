"""
WebSocket router for streaming log entries.

Provides a WebSocket endpoint that allows clients to subscribe to log updates
with optional filters and pagination.
"""

import datetime as dt
from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field, PositiveInt, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, db, schemas

log_ws_router = APIRouter(prefix="/logs-ws", tags=["Logs WS"])


class ParamsInSchema(BaseModel):
    """
    Input schema for log stream filters and pagination.
    """

    pagina: PositiveInt | None = Field(default=1, ge=1, description="Número da página")
    itens_por_pagina: PositiveInt | None = Field(
        default=10, ge=1, description="Itens por página"
    )
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
    Represents a single active WebSocket connection with its current filter params.
    """

    socket: WebSocket
    params: ParamsInSchema


class ConnectionManager:
    """
    Manages active WebSocket connections for the log stream, supporting
    unicast (initial/per-connection updates) and broadcast (fan-out updates).
    """

    def __init__(self) -> None:
        self.active_connections: list[Connection] = []

    def connect(self, ws: WebSocket, params: ParamsInSchema) -> None:
        """
        Register a new WebSocket connection with its initial parameters.

        Args:
            ws: The WebSocket instance.
            params: Initial filter/pagination parameters.
        """
        instance = Connection(socket=ws, params=params)

        if instance not in self.active_connections:
            self.active_connections.append(instance)

    def disconnect(self, ws: WebSocket) -> None:
        """
        Remove a WebSocket connection from the active list.

        Args:
            ws: The WebSocket instance to remove.
        """
        for active_connection in self.active_connections:
            if active_connection.socket == ws:
                self.active_connections.remove(active_connection)
                break

    def change_params(self, ws: WebSocket, params: ParamsInSchema) -> None:
        """
        Update the filter/pagination parameters for a given connection.

        Args:
            ws: The WebSocket instance.
            params: New parameters to apply.
        """
        for active_connection in self.active_connections:
            if active_connection.socket is ws:
                active_connection.params = params
                break

    async def unicast(self, db: AsyncSession, ws: WebSocket) -> None:
        """
        Send a filtered, paginated log list to a single connection.

        Args:
            db: Async database session.
            ws: The WebSocket instance to send data to.
        """
        for a_c in self.active_connections:
            socket, params = a_c.socket, a_c.params

            if socket == ws:
                pagina = params.pagina or 1
                itens_por_pagina = params.itens_por_pagina or 10

                total_items, logs = await cruds.LogCrud.get_all(
                    db=db,
                    page=pagina,
                    items_per_page=itens_por_pagina,
                    method=params.metodo,
                    endpoint=params.endpoint,
                    code=params.codigo,
                    start_date=params.data_inicio,
                    end_date=params.data_fim,
                    start_hour=params.hora_inicio,
                    end_hour=params.hora_fim,
                    protocol=params.protocolo,
                    department=params.setor,
                    customer_name=params.nome_cliente,
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
        """
        Recompute and send filtered/paginated logs to every active connection.

        Filtering is applied in-memory after loading all logs (for simplicity
        and to support many simultaneous filter combinations).
        """
        async with db.AsyncSessionLocal() as session:
            _, all_logs = await cruds.LogCrud.get_all(db=session)
            all_dicts: list[dict[str, Any]] = [log.to_dict() for log in all_logs]

            for a_c in self.active_connections:
                params = a_c.params
                filtered = all_dicts[:]

                # Apply text filters (case-insensitive, partial match)
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

                # Apply date range filters
                if params.data_inicio:
                    start_date = dt.date.fromisoformat(params.data_inicio)
                    filtered = [
                        d for d in filtered if d["criado_em"].date() >= start_date
                    ]
                if params.data_fim:
                    end_date = dt.date.fromisoformat(params.data_fim)
                    filtered = [
                        d for d in filtered if d["criado_em"].date() <= end_date
                    ]
                # Apply time range filters
                if params.hora_inicio:
                    start_time = dt.time.fromisoformat(params.hora_inicio)
                    filtered = [
                        d for d in filtered if d["criado_em"].time() >= start_time
                    ]
                if params.hora_fim:
                    end_time = dt.time.fromisoformat(params.hora_fim)
                    filtered = [
                        d for d in filtered if d["criado_em"].time() <= end_time
                    ]

                # Paginate the filtered results
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

                await a_c.socket.send_json(res.model_dump(mode="json"))


log_manager = ConnectionManager()


@log_ws_router.websocket(path="/")
async def get_logs(
    db: Annotated[AsyncSession, Depends(db.get_db)], ws: WebSocket
) -> None:
    """
    WebSocket endpoint for streaming log entries.

    The client sends an initial JSON payload with filter/pagination parameters,
    receives an initial snapshot, and can send further payloads to update
    the filters. Any invalid payload receives a validation error.
    """
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
                "detail": e.errors,
            }
        )
        await ws.close()
        return
    except WebSocketDisconnect:
        log_manager.disconnect(ws=ws)
        return

    # Main loop: receive new parameters and re-send the filtered snapshot
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
                    "detail": e.errors,
                }
            )
        except WebSocketDisconnect:
            log_manager.disconnect(ws=ws)
            break
