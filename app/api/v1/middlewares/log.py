import time
from .. import crud, database
from zoneinfo import ZoneInfo
from datetime import datetime
from fastapi import Request, status
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware


class LogMiddleware(BaseHTTPMiddleware):
    """Middleware para registrar requisições HTTP em um banco de dados."""

    def __init__(self, app, exclude_paths: list = None):
        """
        Inicializa o middleware de log.

        Args:
            app: A aplicação ASGI.
            exclude_paths: Uma lista de caminhos de URL a serem excluídos do log.
        """
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

    async def dispatch(self, request: Request, call_next):
        """
        Intercepta, processa e registra uma requisição.

        Mede o tempo de processamento da requisição e chama a função de log
        após a conclusão. Exclui caminhos específicos do log.

        Args:
            request: O objeto da requisição.
            call_next: A próxima chamada no pipeline de middleware.

        Returns:
            A resposta da requisição.
        """
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
        """
        Chama a função de log do banco de dados de forma assíncrona.

        Args:
            request: O objeto da requisição.
            status_code: O código de status da resposta.
            process_time: O tempo de processamento da requisição.
        """
        try:
            await self._log_to_database(request, status_code, process_time)
        except Exception as e:
            print(f"Erro ao registrar log: {e}")

    async def _log_to_database(
        self, request: Request, status_code: int, process_time: float
    ):
        """
        Registra os detalhes da requisição no banco de dados de forma assíncrona.

        Obtém uma sessão de banco de dados, cria uma entrada de log e a salva.
        Trata exceções de banco de dados e garante que a sessão seja fechada.

        Args:
            request: O objeto da requisição.
            status_code: O código de status da resposta.
            process_time: O tempo de processamento da requisição.
        """
        db = None
        try:
            # Extrai o protocolo do header x-protocolo
            protocolo = request.headers.get("x-protocolo", "desconhecido")

            now = datetime.now(ZoneInfo("America/Sao_Paulo"))
            async for db in database.get_db():
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
