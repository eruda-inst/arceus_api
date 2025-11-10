from .. import models
from datetime import date, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError


class LogCRUD:
    """CRUD (Create, Read, Update, Delete) para o modelo Log."""

    @staticmethod
    async def create_log(
        db: AsyncSession,
        ip: str,
        http_method: str,
        endpoint: str,
        status_code: int,
        data: date,
        hora: time,
        duracao: float,
        protocolo: str,
    ):
        """
        Cria uma nova entrada de log no banco de dados de forma assíncrona.

        Args:
            db: A sessão do banco de dados.
            ip: O endereço IP da requisição.
            http_method: O método HTTP da requisição.
            endpoint: O endpoint da API que foi acessado.
            status_code: O código de status da resposta HTTP.
            data: A data da requisição.
            hora: A hora da requisição.
            duracao: O tempo de duração da requisição em segundos.
            protocolo: O protocolo de atendimento associado à requisição.

        Returns:
            O objeto de log criado.

        Raises:
            SQLAlchemyError: Se ocorrer um erro durante a operação de banco de dados.
        """
        try:
            log_entry = models.Log(
                ip=ip,
                http_method=http_method,
                endpoint=endpoint,
                status_code=status_code,
                data=data,
                hora=hora,
                duracao=round(duracao, 4),
                protocolo=protocolo,
            )
            db.add(log_entry)
            await db.commit()
            await db.refresh(log_entry)
            return log_entry
        except SQLAlchemyError as e:
            await db.rollback()
            raise e


log_crud = LogCRUD()
