from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class Meta(BaseModel):
    total: int = Field(default=1, ge=1, description="Número total de itens em todas as páginas.")
    page: int = Field(default=1, ge=1, description="Número da página atual na sequência de paginação.")
    per_page: int = Field(default=1, ge=1, description="Número de itens exibidos por página.")


class Links(BaseModel):
    self: Optional[str] = Field(default=None, description="URL da página atual de resultados.")
    next: Optional[str] = Field(default=None, description="URL para a próxima página de resultados, se disponível.")
    prev: Optional[str] = Field(default=None, description="URL para a página anterior de resultados, se disponível.")


class StatusContrato(BaseModel):
    status_contrato: Optional[Literal["P", "A", "I", "N", "D"]] = Field(default="P", description="Status atual do contrato.")


class StatusContratoOut(BaseModel):
    data: StatusContrato


class Contrato(BaseModel):
    id: str = Field(default=None, max_length=11, description="ID único do contrato.")
    status: Optional[Literal["P", "A", "I", "N", "D"]] = Field(default="P", description="Status atual do contrato.")
    contrato: str = Field(default=None, max_length=100, description="Número do contrato.")


class ContratoListOut(BaseModel):
    data: List[Contrato] = Field(default=None, description="Lista de contratos")
    meta: Meta
    links: Links