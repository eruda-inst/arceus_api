import time
from .. import cruds
from ..db import get_db
from zoneinfo import ZoneInfo
from datetime import datetime
from fastapi.logger import logger
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Request, status, Response
from typing import Self, Awaitable, Callable, Any
from starlette.middleware.base import BaseHTTPMiddleware


class LogMiddleware(BaseHTTPMiddleware):
    def __init__(self: Self, app: Any):
        super().__init__(app)
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
        if not any(path.startswith(prefix) for prefix in self.include_prefixes):
            return await call_next(request)
        start_time = time.perf_counter()
        response = None
        try:
            response = await call_next(request)
        except Exception as e:
            await self._log_request(
                request=request,
                codigo=status.HTTP_500_INTERNAL_SERVER_ERROR,
                process_time=time.perf_counter() - start_time,
            )
            raise e
        else:
            await self._log_request(
                request=request,
                codigo=response.status_code,
                process_time=time.perf_counter() - start_time,
            )
        return response

    async def _log_request(self, request: Request, codigo: int, process_time: float):
        try:
            await self._log_to_database(request, codigo, process_time)
        except Exception as e:
            logger.error(f"Erro ao registrar log: {e}")

    async def _log_to_database(
        self, request: Request, codigo: int, process_time: float
    ):
        db = None
        try:
            # Extrai o protocolo do header x-protocolo
            protocolo = request.headers.get("x-protocolo", "---")

            now = datetime.now(ZoneInfo("America/Bahia"))

            async for db in get_db():
                await cruds.log_crud.create_log(
                    db=db,
                    ip=request.client.host if request.client else "---",
                    metodo=request.method,
                    endpoint=request.url.path,
                    codigo=codigo,
                    data=now.date(),
                    hora=now.time(),
                    duracao=process_time,
                    protocolo=protocolo,
                )
                break
        except SQLAlchemyError as e:
            if db:
                await db.rollback()
            logger.error(f"Erro de banco ao registrar log: {e}")
        finally:
            if db is not None:
                await db.close()
