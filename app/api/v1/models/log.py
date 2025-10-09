from .. import database
from sqlalchemy import Column, DateTime, Float, Integer, String


class Log(database.base.Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False)
    duracao = Column(Float, nullable=False)
