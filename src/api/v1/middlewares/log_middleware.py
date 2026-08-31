import asyncio
import re
import time
from collections.abc import Awaitable, Callable
from typing import override

from fastapi import Request, Response
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

        asyncio.create_task(websockets.metric_manager.broadcast())
        asyncio.create_task(websockets.log_manager.broadcast())

        # A response precisa ser refeita
        return Response(
            content=response,
            status_code=res.status_code,
            headers=dict(res.headers),
            media_type=res.media_type,
        )
