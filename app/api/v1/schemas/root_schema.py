from pydantic import BaseModel, HttpUrl, Field


class RootOut(BaseModel):
    docs_url: HttpUrl = Field(
        description="URL para a documentação da API.",
        examples=["http://localhost:8000/docs"],
    )
    redoc_url: HttpUrl = Field(
        description="URL para a documentação da API com redoc.",
        examples=["http://localhost:8000/redoc"],
    )
