"""
Pydantic schemas for the API root endpoint.
"""

from pydantic import BaseModel, Field, HttpUrl


class RootOutSchema(BaseModel):
    """
    Response schema for the root endpoint, providing API metadata.
    """

    titulo: str = Field(description="Título da API", examples=["Título da API"])
    descricao: str = Field(
        description="Descrição da API", examples=["Descrição da API"]
    )
    url_docs: HttpUrl = Field(
        description="URL para acesso à documentação docs",
        examples=["http://localhost:8000/docs"],
    )
    url_redoc: HttpUrl = Field(
        description="URL para acesso à documentação redoc",
        examples=["http://localhost:8000/redoc"],
    )
