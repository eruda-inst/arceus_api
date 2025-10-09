from .. import models
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


class LogCRUD:
    @staticmethod
    def create_log(
        db: Session, ip: str, endpoint: str, status_code: int, duracao: float
    ):
        try:
            log_entry = models.Log(
                ip=ip,
                endpoint=endpoint,
                status_code=status_code,
                datetime=datetime.now(),
                duracao=round(duracao, 4),
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            return log_entry
        except SQLAlchemyError as e:
            db.rollback()
            raise e


log_crud = LogCRUD()
