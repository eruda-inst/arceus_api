from pydantic import BaseModel, Field, HttpUrl


class IndexOut(BaseModel):
    titulo: str = Field(description="Título da API", examples=["Título da API"])
    descricao: str = Field(
        description="Descrição da API", examples=["Descrição da API"]
    )
    docs_url: HttpUrl = Field(
        description="URL para acesso à documentação docs",
        examples=["http://localhost:8000/docs"],
    )
    redoc_url: HttpUrl = Field(
        description="URL para acesso à documentação redoc",
        examples=["http://localhost:8000/redoc"],
    )
