from .. import db
from sqlalchemy import Column, Date, Numeric, Integer, String, Time


class Log(db.base_db.Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, nullable=False)
    metodo = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    codigo = Column(Integer, nullable=False)
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    duracao = Column(Numeric(10, 2), nullable=False)
    protocolo = Column(String, nullable=False)

    payload = Column(String, nullable=False)
    resposta = Column(String, nullable=True)
    url = Column(String, nullable=False)
    cliente = Column(String, nullable=False)
    dominio = Column(String, nullable=False)
    setor = Column(String, nullable=False)
