from .misc import Meta, Links
from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from ..utils import StatusAtendimentoRotulo


class AtendimentoIn(BaseModel):
    id_login: int = Field(description="ID de login do cliente.")
    id_assunto: int = Field(description="ID do assunto do atendimento.")
    id_cliente: int = Field(description="ID do cliente.")
    menssagem: str = Field(description="Mensagem descritiva.")
    origem_endereco: Optional[Literal["C", "L", "CC", "M"]] = Field(default="L", description="Origem de endereço.")
    tipo: Optional[Literal["C", "E"]] = Field(default="C", description="Tipo do atendimento.")
    titulo: str = Field(description="Título do atendimento.")
    prioridade: Optional[Literal["B", "M", "A", "C"]] = Field(default="M", description="Pioridade do atendimento.")
    su_status: Optional[Literal["N", "P", "EP", "S", "C"]] = Field(default="N", description="Status do atendimento.")
    id_ticket_setor: int =  Field(description="Setor do atendimento.")
    id_contrato: int = Field(description="ID de contrato do cliente.")

class Atendimento(BaseModel):
    id: int = Field(description="ID do atendimento.")
    id_assunto: int = Field(description="ID do assunto do atendimento.")
    status: StatusAtendimentoRotulo = Field(description="Status do atendimento.")
    mensagem: str = Field(max_length=999, description="Mensagem descritiva.")
    titulo: str = Field(max_length=200, description="Título do atendimento.")
    data_criacao: str = Field(description="Data de criação do atendimento.")

class AtendimentoOut(BaseModel):
    data: List[Atendimento]
    meta: Meta
    links: Links