from .. import models
from datetime import date, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError


class LogCRUD:
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
