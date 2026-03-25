from .. import db
from sqlalchemy import Column, Date, Numeric, Integer, String, Time


class Log(db.base.Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, nullable=False)
    http_method = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    duracao = Column(Numeric(10, 2), nullable=False)
    protocolo = Column(String, nullable=False)
