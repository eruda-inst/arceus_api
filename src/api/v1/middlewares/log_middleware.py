"""
Middleware for logging API requests and responses.

Captures request/response data for specific API prefixes, extracts metadata,
and persists log entries asynchronously.
"""

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
        # API path prefixes that should be logged
        self.include_prefixes = (
            "/api/v1/cobranca",
            "/api/v1/comercial",
            "/api/v1/financeiro",
            "/api/v1/suporte",
            "/api/v1/triagem",
            "/api/v1/upgrade",
            "/api/v1/vila",
        )
        # Department names corresponding to the prefixes
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
        if not request.url.path.startswith(self.include_prefixes):
            return await call_next(request)

        # Read the request body (will be consumed, so we need to re-attach later)
        payload = await request.body()

        # Measure request processing time
        start_time = time.perf_counter()
        res = await call_next(request)
        end_time = time.perf_counter()

        duration = end_time - start_time

        # Extract and validate the protocol header (must match ^NWT\d{9}$)
        protocol = request.headers.get("x-protocolo")
        if protocol and not re.search(pattern=r"^NWT\d{9}$", string=protocol):
            protocol = None

        http_method = request.method
        status_code = res.status_code
        endpoint = request.url.path

        # Decode payload if present
        payload = payload.decode()
        payload = payload if payload else None

        # Determine the department based on the endpoint path
        setor = None
        for d in self.departments:
            if d in endpoint:
                setor = str(d).capitalize()
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
        asyncio.create_task(websockets.metric_manager.broadcast())
        asyncio.create_task(websockets.log_manager.broadcast())

        # Return the response with the original body and headers
        return Response(
            content=response,
            status_code=res.status_code,
            headers=dict(res.headers),
            media_type=res.media_type,
        )
