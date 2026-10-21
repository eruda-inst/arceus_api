import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import override

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .. import cruds, db, services, ws


class LogMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs incoming requests and outgoing responses for
    specified API path prefixes.
    """

    def __init__(self, app: ASGIApp):
        """
        Initialize the middleware with a list of path prefixes to include
        and corresponding department names.

        Args:
            app: The ASGI application to wrap.
        """
        super().__init__(app)
        self.ALLOWED_ENDPOINTS = (
            "/api/v1/cobranca/faturas-vencidas",
            "/api/v1/comercial/leads",
            "/api/v1/comercial/status-acesso",
            "/api/v1/financeiro/chave-pix",
            "/api/v1/financeiro/credenciais",
            "/api/v1/financeiro/desbloqueio-em-confianca",
            "/api/v1/financeiro/faturas-abertas",
            "/api/v1/financeiro/linha-digitavel",
            "/api/v1/financeiro/tres-faturas-abertas",
            "/api/v1/suporte/atendimentos",
            "/api/v1/suporte/contratos-teste",
            "/api/v1/suporte/contratos",
            "/api/v1/suporte/dados-wifi",
            "/api/v1/suporte/desconectar-cliente",
            "/api/v1/suporte/ip",
            "/api/v1/suporte/limpar-mac",
            "/api/v1/suporte/servidor-dns",
            "/api/v1/suporte/sinal-fibra",
            "/api/v1/suporte/status-conexao",
            "/api/v1/suporte/status-onu",
            "/api/v1/suporte/tem-ipv6",
            "/api/v1/suporte/uptime",
            "/api/v1/triagem/contato-cliente",
            "/api/v1/upgrade/planos-sugeridos",
            "/api/v1/vila/atendimentos",
            "/api/v1/vila/contrato/numero-residencia",
            "/api/v1/vila/contrato/pppoe",
            "/api/v1/vila/dados-wifi",
            "/api/v1/vila/desconectar-cliente",
            "/api/v1/vila/limpar-mac",
            "/api/v1/vila/servidor-dns",
            "/api/v1/vila/sinal-fibra",
            "/api/v1/vila/status-conexao",
            "/api/v1/vila/status-onu",
            "/api/v1/vila/tem-ipv6",
            "/api/v1/vila/uptime",
        )
        self.DEPARTMENTS = (
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
        """
        Process the request, log details, and return the response.

        Only requests whose path starts with one of the configured prefixes
        are logged. The middleware reads the request body, measures duration,
        extracts protocol and department, fetches customer info if a protocol
        is present, and stores a log entry. It also broadcasts updates via
        WebSocket managers.

        Args:
            request: The incoming HTTP request.
            call_next: Callable to invoke the next middleware or endpoint.

        Returns:
            The HTTP response from the downstream application.
        """
        # Skip logging for paths that do not match the configured prefixes
        there_is = False

        for allowed_enpoint in self.ALLOWED_ENDPOINTS:
            if allowed_enpoint in request.url.path:
                there_is = True
                break

        if not there_is:
            return await call_next(request)

        # Read the request body (will be consumed, so we need to re-attach later)
        payload = await request.body()

        # Measure request processing time
        start_time = time.perf_counter()
        res = await call_next(request)
        end_time = time.perf_counter()

        duration = end_time - start_time

        protocol = request.headers.get("x-protocolo")

        http_method = request.method
        status_code = res.status_code

        endpoint = request.url.path
        for allowed_endpoint in self.ALLOWED_ENDPOINTS:
            if allowed_endpoint in endpoint:
                endpoint = allowed_endpoint
                break

        # Decode payload if present
        payload = payload.decode()
        payload = payload if payload else None

        # Determine the department based on the endpoint path
        setor = None
        for department in self.DEPARTMENTS:
            if department in endpoint:
                setor = str(department).capitalize()
                if setor == "Cobranca":
                    setor = "Cobrança"
                break

        # Read the response body (stream) to log it
        response_body = b""
        async for chunk in res.body_iterator:  # type: ignore
            response_body += chunk  # type: ignore

        response = response_body.decode()  # type: ignore

        # --- Cliente IXC ---
        # If a valid protocol exists, fetch the customer name from IXC
        nome_cliente = None
        if protocol:
            cliente = await services.CustomerService.get_ixc_customer(protocol=protocol)
            if cliente:
                nome_cliente = cliente["razao"]

        # Persist the log entry in the database
        async with db.AsyncSessionLocal() as session:
            await cruds.LogCrud.create_log(
                db=session,
                method=http_method,
                endpoint=endpoint,
                code=status_code,
                duration=duration,
                protocol=protocol,
                payload=payload,
                response=response_body.decode(),
                url=str(request.url),
                sector=setor,
                customer_name=nome_cliente,
            )

        # Broadcast metric and log updates via WebSocket (fire-and-forget)
        asyncio.create_task(ws.metric_manager.broadcast())
        asyncio.create_task(ws.log_manager.broadcast())

        # Return the response with the original body and headers
        return Response(
            content=response,
            status_code=res.status_code,
            headers=dict(res.headers),
            media_type=res.media_type,
        )
