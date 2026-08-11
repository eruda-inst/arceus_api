from typing import Annotated

from pydantic import BaseModel, Field, NonNegativeInt, PlainSerializer

Round3Schema = Annotated[
    float, PlainSerializer(lambda v: round(v, 3), return_type=float)
]
Round2Schema = Annotated[
    float, PlainSerializer(lambda v: round(v, 2), return_type=float)
]


class TopEndpointSchema(BaseModel):
    endpoint: str = Field(
        description="Endpoint da requisição", examples=["/suporte/status_conexao"]
    )
    total_requisicoes: NonNegativeInt = Field(
        description="Quantidade de requisições", ge=0, examples=[12]
    )


class TopStatusCodeSchema(BaseModel):
    status_code: NonNegativeInt = Field(
        description="Código HTTP da resposta", examples=[200], ge=0
    )
    total_respostas: NonNegativeInt = Field(
        description="Quantidade de respostas", ge=0, examples=[12]
    )


class TopHourSchema(BaseModel):
    hora: NonNegativeInt = Field(description="Hora da requisição", examples=[13], ge=0)
    total_requisicoes: NonNegativeInt = Field(
        description="Quantidade de requisições", ge=0, examples=[12]
    )


class TopWeekdaySchema(BaseModel):
    dia_semana: str = Field(description="Dia da semana da requisição", examples=["Sáb"])
    total_requisicoes: NonNegativeInt = Field(
        description="Quantidade de requisições", ge=0, examples=[12]
    )


class TopWorstEndpointSchema(BaseModel):
    endpoint: str = Field(
        description="Endpoint da requisição", examples=["/suporte/status_conexao"]
    )
    total_erros: NonNegativeInt = Field(
        description="Quantidade de erros", ge=0, examples=[12]
    )


class TopMonthDaySchema(BaseModel):
    dia_mes: NonNegativeInt = Field(
        description="Dia do mês (1-31)", examples=[15], ge=1, le=31
    )
    total_requisicoes: NonNegativeInt = Field(
        description="Quantidade de requisições", ge=0, examples=[120]
    )


class TopSlowestEndpointSchema(BaseModel):
    endpoint: str = Field(
        description="Endpoint da requisição", examples=["/suporte/status_conexao"]
    )
    duracao: Round3Schema = Field(
        description="Duração entre a requisição, processamento e resposta",
        examples=[0.1234],
    )


class TopHttpMethodSchema(BaseModel):
    metodo_http: str = Field(description="Método HTTP", examples=["GET"])
    total_requisicoes: NonNegativeInt = Field(
        description="Quantidade de requisições", ge=0, examples=[120]
    )


class TopDepartmentSchema(BaseModel):
    setor: str | None = Field(
        description="Setor/departamento responsável pela requisição",
        examples=["Financeiro", "Suporte"],
    )
    total_requisicoes: NonNegativeInt = Field(
        description="Quantidade de requisições", ge=0, examples=[42]
    )


class SuccessStatsSchema(BaseModel):
    total: NonNegativeInt = Field(description="Total de requisições bem-sucedidas")
    percentual: Round2Schema = Field(
        description="Percentual de sucesso (0 a 100)", ge=0, le=100
    )


class ErrorStatsSchema(BaseModel):
    total: NonNegativeInt = Field(description="Total de requisições malsucedidas")
    percentual: Round2Schema = Field(
        description="Percentual de erro (0 a 100)", ge=0, le=100
    )


class ResponseTimeStatsSchema(BaseModel):
    min: Round3Schema = Field(
        description="Menor duração (em segundos)", examples=[0.045]
    )
    avg: Round3Schema = Field(
        description="Duração média (em segundos)", examples=[0.234]
    )
    max: Round3Schema = Field(
        description="Maior duração (em segundos)", examples=[1.567]
    )


class TopClientNameSchema(BaseModel):
    nome_cliente: str | None = Field(
        default=None, description="Nome completo do cliente", examples=["John Doe"]
    )
    total_requisicoes: NonNegativeInt = Field(
        description="Quantidade de requisições", ge=0, examples=[120]
    )
