from .. import database
from sqlalchemy import Column, DateTime, Float, Integer, String, func

Base = database.Base


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    datetime = Column(DateTime, server_default=func.now(), nullable=False)
    duracao = Column(Float, nullable=False)
