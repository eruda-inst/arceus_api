import time
from fastapi import Request
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.database import get_db
from app.api.v1.models.log import Log


class LogsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in [
            "/",
            "/docs",
            "/redoc",
            "/favicon.ico",
            "/openapi.json",
        ]:
            return await call_next(request)

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as e:
            response = None
            raise e
        finally:
            process_time = time.perf_counter() - start_time

            if response:
                try:
                    db = next(get_db())
                    log_entry = Log(
                        ip=request.client.host if request.client else "unknown",
                        endpoint=f"{request.method} {request.url.path}",
                        status_code=response.status_code if response else 500,
                        datetime=datetime.now(),
                        duracao=round(process_time, 4),
                    )
                    db.add(log_entry)
                    db.commit()
                    print(
                        f"Log salvo: {request.method} {request.url.path} - {response.status_code}"
                    )
                except SQLAlchemyError as e:
                    print(f"Erro ao salvar log no banco: {e}")
                    db.rollback()
                except Exception as e:
                    print(f"Erro inesperado ao salvar log: {e}")
                finally:
                    if "db" in locals():
                        db.close()

        return response
