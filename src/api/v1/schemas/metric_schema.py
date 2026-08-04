from typing import Annotated

from pydantic import BaseModel, Field, NonNegativeInt, PlainSerializer

Round3 = Annotated[float, PlainSerializer(lambda v: round(v, 3), return_type=float)]
Round2 = Annotated[float, PlainSerializer(lambda v: round(v, 2), return_type=float)]


class TopEndpoint(BaseModel):
    endpoint: str = Field(
        description="Endpoint da requisição", examples=["/suporte/status_conexao"]
    )
    total_requisicoes: NonNegativeInt = Field(
        description="Quantidade de requisições", ge=0, examples=[12]
    )


class TopStatusCode(BaseModel):
    status_code: NonNegativeInt = Field(
        description="Código HTTP da resposta", examples=[200], ge=0
    )
    total_respostas: NonNegativeInt = Field(
        description="Quantidade de respostas", ge=0, examples=[12]
    )


class TopHour(BaseModel):
    hora: NonNegativeInt = Field(description="Hora da requisição", examples=[13], ge=0)
    total_requisicoes: NonNegativeInt = Field(
        description="Quantidade de requisições", ge=0, examples=[12]
    )


class TopWeekday(BaseModel):
    dia_semana: str = Field(description="Dia da semana da requisição", examples=["Sáb"])
    total_requisicoes: NonNegativeInt = Field(
        description="Quantidade de requisições", ge=0, examples=[12]
    )


class TopWorstEndpoint(BaseModel):
    endpoint: str = Field(
        description="Endpoint da requisição", examples=["/suporte/status_conexao"]
    )
    total_erros: NonNegativeInt = Field(
        description="Quantidade de erros", ge=0, examples=[12]
    )


class TopMonthDay(BaseModel):
    dia_mes: NonNegativeInt = Field(
        description="Dia do mês (1-31)", examples=[15], ge=1, le=31
    )
    total_requisicoes: NonNegativeInt = Field(
        description="Quantidade de requisições", ge=0, examples=[120]
    )


class TopSlowestEndpoint(BaseModel):
    endpoint: str = Field(
        description="Endpoint da requisição", examples=["/suporte/status_conexao"]
    )
    duracao: Round3 = Field(
        description="Duração entre a requisição, processamento e resposta",
        examples=[0.1234],
    )


class TopHttpMethod(BaseModel):
    metodo_http: str = Field(description="Método HTTP", examples=["GET"])
    total_requisicoes: NonNegativeInt = Field(
        description="Quantidade de requisições", ge=0, examples=[120]
    )


class TopDepartment(BaseModel):
    setor: str = Field(
        description="Setor/departamento responsável pela requisição",
        examples=["Financeiro", "Suporte"],
    )
    total_requisicoes: NonNegativeInt = Field(
        description="Quantidade de requisições", ge=0, examples=[42]
    )


class SuccessStats(BaseModel):
    total: NonNegativeInt = Field(description="Total de requisições bem-sucedidas")
    percentual: Round2 = Field(
        description="Percentual de sucesso (0 a 100)", ge=0, le=100
    )


class ErrorStats(BaseModel):
    total: NonNegativeInt = Field(description="Total de requisições malsucedidas")
    percentual: Round2 = Field(description="Percentual de erro (0 a 100)", ge=0, le=100)


class ResponseTimeStats(BaseModel):
    min: Round3 = Field(description="Menor duração (em segundos)", examples=[0.045])
    avg: Round3 = Field(description="Duração média (em segundos)", examples=[0.234])
    max: Round3 = Field(description="Maior duração (em segundos)", examples=[1.567])


class TopClientName(BaseModel):
    nome_cliente: str | None = Field(
        default=None, description="Nome completo do cliente", examples=["John Doe"]
    )
    total_requisicoes: NonNegativeInt = Field(
        description="Quantidade de requisições", ge=0, examples=[120]
    )
