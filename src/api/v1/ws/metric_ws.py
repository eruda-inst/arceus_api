"""
WebSocket router for streaming metric data.

Clients can enroll/unenroll in one or more metrics and receive updates
either on demand (unicast) or via broadcasts triggered by the system.
"""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, db

metric_ws_router = APIRouter(prefix="/metricas-ws", tags=["Métricas WS"])


# Supported actions for incoming messages
Action = Literal["enroll", "unenroll"]

# Supported metric names
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
    """
    Input schema for metric WebSocket messages.

    Attributes:
        action: Either "enroll" (subscribe) or "unenroll" (unsubscribe).
        metric_names: A specific list of metrics or "all".
    """

    action: Action | None = Field(default="enroll", description="Ação a ser executada")
    metric_names: list[MetricNames] | Literal["all"] = Field(
        description="Métricas desejadas"
    )


class ConnectionManager:
    """
    Manages WebSocket subscriptions grouped by metric name.
    """

    def __init__(self) -> None:
        # Map each supported metric to the list of subscribed WebSockets
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
        Subscribe a WebSocket to the given metrics (or all).

        Args:
            ws: The WebSocket instance.
            metric_names: Metrics to subscribe to, or "all".
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
        Unsubscribe a WebSocket from the given metrics (or all).

        Args:
            ws: The WebSocket instance.
            metric_names: Metrics to unsubscribe from, or "all".
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

    async def unicast(
        self,
        db: AsyncSession,
        ws: WebSocket,
        metric_names: list[MetricNames] | Literal["all"],
    ) -> None:
        """
        Send the current values for the requested metrics to a single WebSocket.

        Args:
            db: Async database session.
            ws: The WebSocket instance.
            metric_names: Metrics to include, or "all".
        """
        message = {}

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

    async def broadcast(self) -> None:
        """
        Send updated values to all connections subscribed to each metric.

        Only metrics with at least one subscriber trigger a database query.
        """
        async with db.AsyncSessionLocal() as session:
            if self.active_connections["erros"]:
                erros = await cruds.MetricCrud.get_error_stats(db=session)
                for connection in self.active_connections["erros"]:
                    await connection.send_json({"erros": erros.model_dump()})
            if self.active_connections["sucessos"]:
                sucessos = await cruds.MetricCrud.get_success_stats(db=session)
                for connection in self.active_connections["sucessos"]:
                    await connection.send_json({"sucessos": sucessos.model_dump()})
            if self.active_connections["tempo_resposta"]:
                tempo_resposta = await cruds.MetricCrud.get_res_time(db=session)
                for connection in self.active_connections["tempo_resposta"]:
                    await connection.send_json(
                        {"tempo_resposta": tempo_resposta.model_dump()}
                    )
            if self.active_connections["top_clientes"]:
                top_clientes = await cruds.MetricCrud.get_top_clients(db=session)
                for connection in self.active_connections["top_clientes"]:
                    await connection.send_json(
                        {"top_clientes": top_clientes.model_dump()}
                    )
            if self.active_connections["top_dias_mes"]:
                top_dias_mes = await cruds.MetricCrud.get_top_month_days(db=session)
                for connection in self.active_connections["top_dias_mes"]:
                    await connection.send_json(
                        {"top_dias_mes": top_dias_mes.model_dump()}
                    )
            if self.active_connections["top_dias_semana"]:
                top_dias_semana = await cruds.MetricCrud.get_top_weekdays(db=session)
                for connection in self.active_connections["top_dias_semana"]:
                    await connection.send_json(
                        {"top_dias_semana": top_dias_semana.model_dump()}
                    )
            if self.active_connections["top_endpoints"]:
                top_endpoints = await cruds.MetricCrud.get_top_endpoints(db=session)
                for connection in self.active_connections["top_endpoints"]:
                    await connection.send_json(
                        {"top_endpoints": top_endpoints.model_dump()}
                    )
            if self.active_connections["top_endpoints_mais_lentos"]:
                top_endpoints_mais_lentos = (
                    await cruds.MetricCrud.get_top_slowest_endpoints(db=session)
                )
                for connection in self.active_connections["top_endpoints_mais_lentos"]:
                    await connection.send_json(
                        {
                            "top_endpoints_mais_lentos": top_endpoints_mais_lentos.model_dump()
                        }
                    )
            if self.active_connections["top_horas"]:
                top_horas = await cruds.MetricCrud.get_top_hours(db=session)
                for connection in self.active_connections["top_horas"]:
                    await connection.send_json({"top_horas": top_horas.model_dump()})
            if self.active_connections["top_metodos_http"]:
                top_metodos_http = await cruds.MetricCrud.get_top_http_methods(
                    db=session
                )
                for connection in self.active_connections["top_metodos_http"]:
                    await connection.send_json(
                        {"top_metodos_http": top_metodos_http.model_dump()}
                    )
            if self.active_connections["top_piores_endpoints"]:
                top_piores_endpoints = await cruds.MetricCrud.get_worst_endpoints(
                    db=session
                )
                for connection in self.active_connections["top_piores_endpoints"]:
                    await connection.send_json(
                        {"top_piores_endpoints": top_piores_endpoints.model_dump()}
                    )
            if self.active_connections["top_setores"]:
                top_setores = await cruds.MetricCrud.get_top_departments(db=session)
                for connection in self.active_connections["top_setores"]:
                    await connection.send_json(
                        {"top_setores": top_setores.model_dump()}
                    )
            if self.active_connections["top_status_codes"]:
                top_status_codes = await cruds.MetricCrud.get_top_status_codes(
                    db=session
                )
                for connection in self.active_connections["top_status_codes"]:
                    await connection.send_json(
                        {"top_status_codes": top_status_codes.model_dump()}
                    )
            if self.active_connections["total_atendimentos"]:
                total_atendimentos = await cruds.MetricCrud.get_total_services(
                    db=session
                )
                for connection in self.active_connections["total_atendimentos"]:
                    await connection.send_json(
                        {"total_atendimentos": total_atendimentos.model_dump()}
                    )
            if self.active_connections["total_requisicoes"]:
                total_requisicoes = await cruds.MetricCrud.get_total_reqs(db=session)
                for connection in self.active_connections["total_requisicoes"]:
                    await connection.send_json(
                        {"total_requisicoes": total_requisicoes.model_dump()}
                    )


metric_manager: ConnectionManager = ConnectionManager()


@metric_ws_router.websocket(path="/")
async def get_metric(
    db: Annotated[AsyncSession, Depends(db.get_db)], ws: WebSocket
) -> None:
    """
    WebSocket endpoint for streaming metrics.

    Clients send an initial payload specifying which metrics to enroll in,
    receive an initial snapshot, and can then send additional payloads to
    enroll/unenroll in other metrics. Invalid payloads receive a validation error.
    """
    await ws.accept()

    try:
        raw = await ws.receive_json()
        initial_message = MessageInSchema(**raw)
        metric_manager.enroll(ws=ws, metric_names=initial_message.metric_names)
        await metric_manager.unicast(
            db=db, ws=ws, metric_names=initial_message.metric_names
        )
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
        metric_manager.unenroll(ws=ws, metric_names="all")
        return

    # Main loop: process enroll/unenroll actions
    while True:
        try:
            raw = await ws.receive_json()
            message = MessageInSchema(**raw)

            if message.action == "enroll":
                metric_manager.enroll(ws=ws, metric_names=message.metric_names)
            else:
                metric_manager.unenroll(ws=ws, metric_names=message.metric_names)

            await metric_manager.unicast(
                db=db, ws=ws, metric_names=message.metric_names
            )
        except ValidationError as e:
            await ws.send_json(
                {
                    "type": "error",
                    "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
                    "detail": e.errors,
                }
            )
        except WebSocketDisconnect:
            metric_manager.unenroll(ws=ws, metric_names="all")
            break
