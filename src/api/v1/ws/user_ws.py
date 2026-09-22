"""
WebSocket router for streaming user data.

Provides a WebSocket endpoint that allows clients to subscribe to user list
updates with optional filters and pagination.
"""

from dataclasses import dataclass
from typing import Annotated, Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field, PositiveInt, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import joinedload

from .. import cruds, db, models, schemas

user_ws_router = APIRouter(prefix="/usuarios-ws", tags=["Usuários WS"])


class Params(BaseModel):
    """
    Input schema for user stream filters and pagination.
    """

    pagina: PositiveInt | None = Field(default=1, ge=1, description="Número da página")
    itens_por_pagina: PositiveInt | None = Field(
        default=10, ge=1, description="Itens por página"
    )
    nome: str | None = Field(
        default=None, description="Filtro parcial por nome do usuário"
    )
    email: str | None = Field(
        default=None, description="Filtro parcial por e-mail do usuário"
    )
    ativo: bool | None = Field(default=None, description="Filtro por status do usuário")
    nome_grupo: str | None = Field(
        default=None, description="Filtro parcial por nome do grupo"
    )


@dataclass
class Connection:
    """
    Represents a single active WebSocket connection with its current filter params.
    """

    socket: WebSocket
    params: Params


class ConnectionManager:
    """
    Manages active WebSocket connections for the user stream, supporting
    unicast (initial/per-connection updates) and broadcast (fan-out updates).
    """

    def __init__(self) -> None:
        self.active_connections: list[Connection] = []

    def connect(self, ws: WebSocket, params: Params) -> None:
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

    def change_params(self, ws: WebSocket, params: Params) -> None:
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
        Send a filtered, paginated user list to a single connection.

        Args:
            db: Async database session.
            ws: The WebSocket instance to send data to.
        """
        for a_c in self.active_connections:
            socket, params = a_c.socket, a_c.params

            if socket == ws:
                pagina = params.pagina or 1
                itens_por_pagina = params.itens_por_pagina or 10

                total_items, users = await cruds.UserCrud.get_all_by(
                    db=db,
                    page=pagina,
                    items_per_page=itens_por_pagina,
                    name=params.nome,
                    email=params.email,
                    active=params.ativo,
                    group_name=params.nome_grupo,
                )

                res = schemas.ListOutSchema[schemas.UserOutSchema](
                    data=[schemas.UserOutSchema.model_validate(u) for u in users],
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
        Recompute and send filtered/paginated users to every active connection.

        Filtering is applied in-memory after loading all users (for simplicity
        and to support many simultaneous filter combinations).
        """
        async with db.AsyncSessionLocal() as session:
            # Eagerly load groups to avoid lazy-loading issues
            stmt = select(models.UserModel).options(joinedload(models.UserModel.grupo))
            result = await session.execute(stmt)
            users = result.unique().scalars().all()

            all_dicts: list[dict[str, Any]] = []
            for user in users:
                d = user.to_dict()
                d["nome_grupo"] = user.grupo.nome
                all_dicts.append(d)

            for a_c in self.active_connections:
                params = a_c.params
                filtered = all_dicts[:]

                # Apply text filters (case-insensitive, partial match)
                if params.nome:
                    search = params.nome.lower()
                    filtered = [d for d in filtered if search in d["nome"].lower()]
                if params.email:
                    search = params.email.lower()
                    filtered = [d for d in filtered if search in d["email"].lower()]
                if params.ativo is not None:
                    filtered = [d for d in filtered if d["ativo"] == params.ativo]
                if params.nome_grupo:
                    search = params.nome_grupo.lower()
                    filtered = [
                        d for d in filtered if search in d["nome_grupo"].lower()
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
                        schemas.UserOutSchema.model_validate(d).model_dump()
                        for d in paginated_dicts
                    ],
                    meta=schemas.MetaOutSchema(
                        pagina_atual=page,
                        itens_por_pagina=items_per_page,
                        total_itens=total_items,
                    ),
                )

                await a_c.socket.send_json(res.model_dump(mode="json"))


user_manager = ConnectionManager()


@user_ws_router.websocket(path="/")
async def get(db: Annotated[AsyncSession, Depends(db.get_db)], ws: WebSocket) -> None:
    """
    WebSocket endpoint for streaming users.

    The client sends an initial JSON payload with filter/pagination parameters,
    receives an initial snapshot, and can send further payloads to update
    the filters. Any invalid payload receives a validation error.
    """
    await ws.accept()

    try:
        raw = await ws.receive_json()
        initial_params = Params(**raw)
        user_manager.connect(ws=ws, params=initial_params)
        await user_manager.unicast(db=db, ws=ws)
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
        user_manager.disconnect(ws=ws)
        return

    # Main loop: receive new parameters and re-send the filtered snapshot
    while True:
        try:
            raw = await ws.receive_json()
            params = Params(**raw)
            user_manager.change_params(ws=ws, params=params)
            await user_manager.unicast(db=db, ws=ws)
        except ValidationError as e:
            await ws.send_json(
                {
                    "type": "error",
                    "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
                    "detail": e.errors,
                }
            )
        except WebSocketDisconnect:
            user_manager.disconnect(ws=ws)
            break
