from .. import models
from zoneinfo import ZoneInfo
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError


class LogCRUD:
    """CRUD (Create, Read, Update, Delete) para o modelo Log."""

    @staticmethod
    async def create_log(
        db: AsyncSession,
        ip: str,
        method: str,
        endpoint: str,
        status_code: int,
        duracao: float,
    ):
        """
        Cria uma nova entrada de log no banco de dados de forma assíncrona.

        Args:
            db: A sessão do banco de dados.
            ip: O endereço IP da requisição.
            method: O método HTTP da requisição.
            endpoint: O endpoint da API que foi acessado.
            status_code: O código de status da resposta HTTP.
            duracao: O tempo de duração da requisição em segundos.

        Returns:
            O objeto de log criado.

        Raises:
            SQLAlchemyError: Se ocorrer um erro durante a operação de banco de dados.
        """
        try:
            log_entry = models.Log(
                ip=ip,
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                datetime=datetime.now(ZoneInfo("America/Sao_Paulo")).replace(
                    tzinfo=None
                ),
                duracao=round(duracao, 4),
            )
            db.add(log_entry)
            await db.commit()
            await db.refresh(log_entry)
            return log_entry
        except SQLAlchemyError as e:
            await db.rollback()
            raise e


log_crud = LogCRUD()
