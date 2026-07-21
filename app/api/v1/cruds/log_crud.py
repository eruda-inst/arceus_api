from .. import models
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class LogCRUD:
    @staticmethod
    async def create_log(
        db: AsyncSession,
        metodo: str,
        endpoint: str,
        codigo: int,
        duracao: float,
        protocolo: str | None,
        payload: str | None,
        resposta: str | None,
        url: str,
        setor: str | None,
        nome_cliente: str | None,
    ):
        try:
            log_entry = models.Log(
                metodo=metodo,
                endpoint=endpoint,
                codigo=codigo,
                duracao=round(duracao, 4),
                protocolo=protocolo,
                payload=payload,
                resposta=resposta,
                url=url,
                setor=setor,
                nome_cliente=nome_cliente,
            )
            db.add(log_entry)
            await db.commit()
            await db.refresh(log_entry)
            return log_entry
        except SQLAlchemyError as e:
            await db.rollback()
            raise e


log_crud = LogCRUD()
