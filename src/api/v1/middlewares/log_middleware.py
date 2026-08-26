import asyncio
import re
import time
from collections.abc import Awaitable, Callable
from typing import override

from fastapi import Request, Response
from fastapi.logger import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .. import cruds, db, services, websockets


class LogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.include_prefixes = (
            "/api/v1/cobranca",
            "/api/v1/comercial",
            "/api/v1/financeiro",
            "/api/v1/suporte",
            "/api/v1/triagem",
            "/api/v1/upgrade",
            "/api/v1/vila",
        )
        self.departments = (
            "cobranca",
            "comercial",
            "financeiro",
            "suporte",
            "triagem",
            "upgrade",
            "vila",
        )

    async def _broadcast_metrics(self):
        async with db.AsyncSessionLocal() as session:
            erros = await cruds.MetricCrud.get_error_stats(db=session)
            await websockets.manager.broadcast(
                metric_names=["erros"], message={"erros": erros.model_dump()}
            )

            sucessos = await cruds.MetricCrud.get_success_stats(db=session)
            await websockets.manager.broadcast(
                metric_names=["sucessos"], message={"sucessos": sucessos.model_dump()}
            )

            tempo_resposta = await cruds.MetricCrud.get_res_time(db=session)
            await websockets.manager.broadcast(
                metric_names=["tempo_resposta"],
                message={"tempo_resposta": tempo_resposta.model_dump()},
            )

            top_clientes = await cruds.MetricCrud.get_top_clients(db=session)
            await websockets.manager.broadcast(
                metric_names=["top_clientes"],
                message={"top_clientes": top_clientes.model_dump()},
            )

            top_dias_mes = await cruds.MetricCrud.get_top_month_days(db=session)
            await websockets.manager.broadcast(
                metric_names=["top_dias_mes"],
                message={"top_dias_mes": top_dias_mes.model_dump()},
            )

            top_dias_semana = await cruds.MetricCrud.get_top_weekdays(db=session)
            await websockets.manager.broadcast(
                metric_names=["top_dias_semana"],
                message={"top_dias_semana": top_dias_semana.model_dump()},
            )

            top_endpoints = await cruds.MetricCrud.get_top_endpoints(db=session)
            await websockets.manager.broadcast(
                metric_names=["top_endpoints"],
                message={"top_endpoints": top_endpoints.model_dump()},
            )

            top_endpoints_mais_lentos = (
                await cruds.MetricCrud.get_top_slowest_endpoints(db=session)
            )
            await websockets.manager.broadcast(
                metric_names=["top_endpoints_mais_lentos"],
                message={
                    "top_endpoints_mais_lentos": top_endpoints_mais_lentos.model_dump()
                },
            )

            top_horas = await cruds.MetricCrud.get_top_hours(db=session)
            await websockets.manager.broadcast(
                metric_names=["top_horas"],
                message={"top_horas": top_horas.model_dump()},
            )

            top_metodos_http = await cruds.MetricCrud.get_top_http_methods(db=session)
            await websockets.manager.broadcast(
                metric_names=["top_metodos_http"],
                message={"top_metodos_http": top_metodos_http.model_dump()},
            )

            top_piores_endpoints = await cruds.MetricCrud.get_worst_endpoints(
                db=session
            )
            await websockets.manager.broadcast(
                metric_names=["top_piores_endpoints"],
                message={"top_piores_endpoints": top_piores_endpoints.model_dump()},
            )

            top_setores = await cruds.MetricCrud.get_top_departments(db=session)
            await websockets.manager.broadcast(
                metric_names=["top_setores"],
                message={"top_setores": top_setores.model_dump()},
            )

            top_status_codes = await cruds.MetricCrud.get_top_status_codes(db=session)
            await websockets.manager.broadcast(
                metric_names=["top_status_codes"],
                message={"top_status_codes": top_status_codes.model_dump()},
            )

            total_atendimentos = await cruds.MetricCrud.get_total_services(db=session)
            await websockets.manager.broadcast(
                metric_names=["total_atendimentos"],
                message={"total_atendimentos": total_atendimentos.model_dump()},
            )

            total_requisicoes = await cruds.MetricCrud.get_total_reqs(db=session)
            await websockets.manager.broadcast(
                metric_names=["total_requisicoes"],
                message={"total_requisicoes": total_requisicoes.model_dump()},
            )

    @override
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:

        if not request.url.path.startswith(self.include_prefixes):
            return await call_next(request)

        # Isto deve estar antes da chamada da rota, i.e., "await call_enxt(request)"
        payload = await request.body()

        start_time = time.perf_counter()
        res = await call_next(request)
        end_time = time.perf_counter()

        duration = end_time - start_time
        url = request.url

        protocol = request.headers.get("x-protocolo")
        if protocol and not re.search(pattern=r"^NWT\d{9}$", string=protocol):
            protocol = None

        http_method = request.method
        status_code = res.status_code
        endpoint = request.url.path

        payload = payload.decode()
        payload = payload if payload else None

        setor = None
        for d in self.departments:
            if d in endpoint:
                setor = str(d).capitalize()
                if setor == "Cobranca":
                    setor = "Cobrança"
                break

        response_body = b""
        async for chunk in res.body_iterator:  # type: ignore
            response_body += chunk  # type: ignore

        response = response_body.decode()  # type: ignore

        # --- Cliente IXC ---
        nome_cliente = None
        if protocol:
            cliente = await services.ClientService.get_cliente_ixc(protocolo=protocol)
            if cliente:
                nome_cliente = cliente["razao"]

        try:
            async with db.AsyncSessionLocal() as session:
                await cruds.LogCrud.create_log(
                    db=session,
                    metodo=http_method,
                    endpoint=endpoint,
                    codigo=status_code,
                    duracao=duration,
                    protocolo=protocol,
                    payload=payload,
                    resposta=response_body.decode(),
                    url=str(request.url),
                    setor=setor,
                    nome_cliente=nome_cliente,
                )
        except Exception as e:
            logger.error("Failed to write log entry: %s", e, exc_info=True)

        asyncio.create_task(self._broadcast_metrics())

        # A response precisa ser refeita
        return Response(
            content=response_body,
            status_code=res.status_code,
            headers=dict(res.headers),
            media_type=res.media_type,
        )
