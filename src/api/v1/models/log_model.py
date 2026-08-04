from sqlalchemy import TIMESTAMP, Column, Integer, Numeric, String, func

from .. import db


class Log(db.base_db.Base):
    __tablename__ = "logs"

    # Métodos utilizados para filtro são indexados (i.e., index=True)
    # Parãmetros posicionais 'nullable' e 'unique' não possuem valor padrão, devem ser passados
    id = Column(
        type_=Integer, primary_key=True, index=True, unique=True, nullable=False
    )
    metodo = Column(type_=String, unique=False, nullable=False, index=True)
    endpoint = Column(type_=String, unique=False, nullable=False, index=True)
    codigo = Column(type_=Integer, unique=False, nullable=False, index=True)
    duracao = Column(type_=Numeric(10, 3), unique=False, nullable=False)
    protocolo = Column(type_=String, unique=False, nullable=True, index=True)
    payload = Column(type_=String, unique=False, nullable=True)
    resposta = Column(type_=String, unique=False, nullable=False)
    url = Column(type_=String, unique=False, nullable=False)
    setor = Column(type_=String, unique=False, nullable=False, index=True)
    nome_cliente = Column(type_=String, unique=False, nullable=True, index=True)

    criado_em = Column(
        type_=TIMESTAMP(timezone=True),
        server_default=func.timezone("America/Bahia", func.now()),
        unique=False,
        nullable=False,
        index=True,
    )
