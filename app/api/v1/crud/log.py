from .. import models
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


class LogCRUD:
    """CRUD (Create, Read, Update, Delete) para o modelo Log."""

    @staticmethod
    def create_log(
        db: Session, ip: str, endpoint: str, status_code: int, duracao: float
    ):
        """
        Cria uma nova entrada de log no banco de dados.

        Args:
            db: A sessão do banco de dados.
            ip: O endereço IP da requisição.
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
