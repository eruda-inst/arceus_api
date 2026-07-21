import re
import time
from .. import cruds, db, services
from starlette.types import ASGIApp
from fastapi import Request, Response
from typing import Awaitable, Callable
from starlette.middleware.base import BaseHTTPMiddleware


class LogMiddleware(BaseHTTPMiddleware):
    _include_prefixes = (
        "/api/v1/cobranca",
        "/api/v1/comercial",
        "/api/v1/financeiro",
        "/api/v1/suporte",
        "/api/v1/triagem",
        "/api/v1/upgrade",
        "/api/v1/vila",
    )
    _departments = [
        "cobrança",
        "comercial",
        "financeiro",
        "suporte",
        "triagem",
        "upgrade",
        "vila",
    ]

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ):
        if not request.url.path.startswith(self._include_prefixes):
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

        setor = [d.capitalize() for d in self._departments if d in endpoint][0]

        response_body = b""
        async for chunk in res.body_iterator:  # type: ignore
            response_body += chunk  # type: ignore

        response = response_body.decode()  # type: ignore

        # --- Cliente IXC ---
        nome_cliente = None
        if protocol:
            cliente = await services.ClienteService.get_cliente_ixc(protocolo=protocol)
            if cliente:
                nome_cliente = cliente["razao"]

        async for session in db.get_db():
            await cruds.log_crud.create_log(
                db=session,
                metodo=http_method,
                endpoint=endpoint,
                codigo=status_code,
                duracao=duration,
                protocolo=protocol,
                payload=payload,
                resposta=response,  # type: ignore
                url=str(url),
                setor=setor,
                nome_cliente=nome_cliente,
            )

        # A response precisa ser refeita
        return Response(
            content=response_body,
            status_code=res.status_code,
            headers=dict(res.headers),
            media_type=res.media_type,
        )
