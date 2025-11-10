from .. import database
from sqlalchemy import Column, Date, Float, Integer, String, Time


class Log(database.base.Base):
    """
    Modelo SQLAlchemy para a tabela 'logs'.

    Esta tabela armazena registros de requisições HTTP feitas à API.

    Atributos:
        id: Chave primária autoincrementável.
        ip: Endereço IP do cliente que fez a requisição.
        http_method: O método HTTP utilizado na requisição (e.g., 'GET').
        endpoint: O endpoint da API que foi acessado (e.g., 'GET /items/').
        status_code: O código de status HTTP da resposta.
        data: A data de quando a requisição foi registrada.
        hora: A hora de quando a requisição foi registrada.
        duracao: O tempo de processamento da requisição em segundos.
        protocolo: O protocolo de atendimento associado à requisição.
    """

    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, nullable=False)
    http_method = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    data = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    duracao = Column(Float, nullable=False)
    protocolo = Column(String, nullable=False)
