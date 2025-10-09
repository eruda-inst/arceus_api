import time
import asyncio
from .. import crud
from fastapi import Request
from app.api.v1 import database
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware


class LogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/",
            "/docs",
            "/redoc",
            "/favicon.ico",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        start_time = time.perf_counter()
        response = None

        try:
            response = await call_next(request)
        except Exception as e:
            await self._log_request(
                request=request,
                status_code=500,
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
            await asyncio.to_thread(
                self._log_to_database, request, status_code, process_time
            )
        except Exception as e:
            print(f"Erro ao registrar log: {e}")

    def _log_to_database(self, request: Request, status_code: int, process_time: float):
        try:
            db = next(database.get_db())
            crud.log_crud.create_log(
                db=db,
                ip=request.client.host if request.client else "unknown",
                endpoint=f"{request.method} {request.url.path}",
                status_code=status_code,
                duracao=process_time,
            )
        except SQLAlchemyError as e:
            print(f"Erro de banco ao registrar log: {e}")
        finally:
            if "db" in locals():
                db.close()
