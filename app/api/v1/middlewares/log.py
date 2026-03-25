import time
from .. import crud
from ..db import get_db
from zoneinfo import ZoneInfo
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Self, Awaitable, Callable, Any
from fastapi import Request, status, Response
from starlette.middleware.base import BaseHTTPMiddleware


class LogMiddleware(BaseHTTPMiddleware):
    def __init__(self: Self, app: Any, exclude_paths: List[str] = []):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/",
            "/docs",
            "/redoc",
            "/favicon.ico",
            "/openapi.json",
        ]
        self.include_prefixes = [
            "/api/v1/suporte",
            "/api/v1/comercial",
            "/api/v1/financeiro",
            "/api/v1/triagem",
            "/api/v1/cobranca",
        ]

    async def dispatch(
        self: Self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ):
        path = request.url.path
        if path in self.exclude_paths or not any(
            path.startswith(prefix) for prefix in self.include_prefixes
        ):
            return await call_next(request)
        start_time = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
        except Exception as e:
            await self._log_request(
                request=request,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                process_time=time.perf_counter() - start_time,
            )
            raise e
        else:
            await self._log_request(
                request=request,
                status_code=response.status_code,
                process_time=time.perf_counter() - start_time,
            )
        return response

    async def _log_request(
        self, request: Request, status_code: int, process_time: float
    ):
        try:
            await self._log_to_database(request, status_code, process_time)
        except Exception as e:
            print(f"Erro ao registrar log: {e}")

    async def _log_to_database(
        self, request: Request, status_code: int, process_time: float
    ):
        db = None
        try:
            # Extrai o protocolo do header x-protocolo
            protocolo = request.headers.get("x-protocolo", "desconhecido")

            now = datetime.now(ZoneInfo("America/Sao_Paulo"))

            async for db in get_db():
                await crud.log_crud.create_log(
                    db=db,
                    ip=request.client.host if request.client else "desconhecido",
                    http_method=request.method,
                    endpoint=request.url.path,
                    status_code=status_code,
                    data=now.date(),
                    hora=now.time(),
                    duracao=process_time,
                    protocolo=protocolo,
                )
                break
        except SQLAlchemyError as e:
            print(f"Erro de banco ao registrar log: {e}")
        finally:
            if db is not None:
                await db.close()
