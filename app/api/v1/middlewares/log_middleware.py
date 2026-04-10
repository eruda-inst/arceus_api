import time
from .. import cruds
from ..db import get_db
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi.logger import logger
from fastapi import Request, Response
from sqlalchemy.exc import SQLAlchemyError
from typing import Awaitable, Callable, Any
from starlette.middleware.base import BaseHTTPMiddleware


INCLUDE_PREFIXES = (
    "/api/v1/suporte",
    "/api/v1/comercial",
    "/api/v1/financeiro",
    "/api/v1/triagem",
    "/api/v1/cobranca",
)


class LogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any):
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ):
        if not request.url.path.startswith(INCLUDE_PREFIXES):
            return await call_next(request)

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            await self._log_request(
                request,
                status_code=500,
                process_time=time.perf_counter() - start_time,
            )
            raise

        await self._log_request(
            request,
            status_code=response.status_code,
            process_time=time.perf_counter() - start_time,
        )
        return response

    async def _log_request(
        self, request: Request, status_code: int, process_time: float
    ):
        try:
            await self._log_to_database(request, status_code, process_time)
        except Exception as err:
            logger.error(f"Erro ao registrar log: {err}")

    async def _log_to_database(
        self, request: Request, status_code: int, process_time: float
    ):
        protocolo = request.headers.get("x-protocolo", "---")
        now = datetime.now(ZoneInfo("America/Bahia"))

        async for db in get_db():
            try:
                await cruds.log_crud.create_log(
                    db=db,
                    ip=request.client.host if request.client else "---",
                    metodo=request.method,
                    endpoint=request.url.path,
                    codigo=status_code,
                    data=now.date(),
                    hora=now.time(),
                    duracao=process_time,
                    protocolo=protocolo,
                )
            except SQLAlchemyError as err:
                await db.rollback()
                logger.error(f"Erro de banco ao registrar log: {err}")
            finally:
                await db.close()
            break
