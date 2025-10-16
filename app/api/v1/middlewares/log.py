import time
from .. import crud
from fastapi import Request
from app.api.v1 import database
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
            async for db in database.get_db():
                await crud.log_crud.create_log(
                    db=db,
                    ip=request.client.host if request.client else "unknown",
                    http_method=request.method,
                    endpoint=request.url.path,
                    status_code=status_code,
                    duracao=process_time,
                )
                break
        except SQLAlchemyError as e:
            print(f"Erro de banco ao registrar log: {e}")
        finally:
            if db is not None:
                await db.close()
