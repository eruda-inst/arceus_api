"""
SQLAlchemy model for the Log table.

Stores API request/response logs including timing, status, and client info.
"""

from typing import Any

from sqlalchemy import TIMESTAMP, Column, Integer, Numeric, String, func

from .. import db

# Columns used for filtering are indexed (i.e., index=True)


class LogModel(db.base_db.Base):
    """
    Represents a log entry for an API request.

    Attributes:
        id: Primary key.
        metodo: HTTP method used.
        endpoint: API endpoint path.
        codigo: HTTP status code returned.
        duracao: Request duration in seconds.
        protocolo: Protocol identifier (e.g., NWT...).
        payload: Request body.
        resposta: Response body.
        url: Full request URL.
        setor: Department or sector derived from the endpoint.
        nome_cliente: Customer name fetched from IXC, if available.
        criado_em: Timestamp when the log was created.
    """

    __tablename__ = "logs"

    id = Column(type_=Integer, primary_key=True, autoincrement=True)
    metodo = Column(type_=String, nullable=False, index=True)
    endpoint = Column(type_=String, nullable=False, index=True)
    codigo = Column(type_=Integer, nullable=False, index=True)
    duracao = Column(type_=Numeric(10, 3), nullable=False)
    protocolo = Column(type_=String, index=True)
    payload = Column(type_=String)
    resposta = Column(type_=String, nullable=False)
    url = Column(type_=String, nullable=False)
    setor = Column(type_=String, nullable=False, index=True)
    nome_cliente = Column(type_=String, index=True)

    criado_em = Column(
        type_=TIMESTAMP(timezone=True),
        server_default=func.timezone("America/Bahia", func.now()),
        nullable=False,
        index=True,
    )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model instance to a dictionary.

        Returns:
            A dictionary containing all column values.
        """
        return {
            "id": self.id,
            "metodo": self.metodo,
            "endpoint": self.endpoint,
            "codigo": self.codigo,
            "duracao": self.duracao,
            "protocolo": self.protocolo,
            "payload": self.payload,
            "resposta": self.resposta,
            "url": self.url,
            "setor": self.setor,
            "nome_cliente": self.nome_cliente,
            "criado_em": self.criado_em,
        }
