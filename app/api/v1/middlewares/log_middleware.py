import time
import json
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

        body_bytes = await request.body()
        payload_str = self._format_payload(body_bytes)

        try:
            response = await call_next(request)
        except Exception:
            await self._log_request(
                request,
                status_code=500,
                process_time=time.perf_counter() - start_time,
                payload=payload_str,
            )
            raise

        await self._log_request(
            request,
            status_code=response.status_code,
            process_time=time.perf_counter() - start_time,
            payload=payload_str,
        )
        return response

    async def _log_request(
        self,
        request: Request,
        status_code: int,
        process_time: float,
        payload: str,
    ):
        try:
            await self._log_to_database(request, status_code, process_time, payload)
        except Exception as err:
            logger.error(f"Erro ao registrar log: {err}")

    async def _log_to_database(
        self,
        request: Request,
        status_code: int,
        process_time: float,
        payload: str,
    ):
        protocolo = request.headers.get("x-protocolo", "---")
        cliente = request.headers.get("user-agent", "---")
        dominio = request.headers.get("host", "---")
        url_completa = str(request.url)

        setor = "---"
        path = request.url.path
        if "/suporte" in path:
            setor = "Suporte"
        elif "/comercial" in path:
            setor = "Comercial"
        elif "/financeiro" in path:
            setor = "Financeiro"
        elif "/triagem" in path:
            setor = "Triagem"
        elif "/cobranca" in path:
            setor = "Cobrança"

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
                    payload=payload,
                    url=url_completa,
                    cliente=cliente,
                    dominio=dominio,
                    setor=setor,
                )
            except SQLAlchemyError as err:
                await db.rollback()
                logger.error(f"Erro de banco ao registrar log: {err}")
            finally:
                await db.close()
            break

    @staticmethod
    def _format_payload(body_bytes: bytes) -> str:
        if not body_bytes:
            return "---"
        try:
            # Tenta decodificar e validar como JSON
            body_json = json.loads(body_bytes.decode("utf-8"))
            return json.dumps(obj=body_json, ensure_ascii=False, separators=(",", ":"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            # Se não for JSON válido, retorna representação segura
            return body_bytes.decode("utf-8", errors="replace")[
                :1000
            ]  # limite de segurança
