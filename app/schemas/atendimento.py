from .misc import Meta, Links
from typing import Optional, List
from pydantic import BaseModel, Field
from ..utils import TipoCod, SuStatusCod, PrioridadeCod, OrigemEnderecoCod, StatusAtendimentoRot

ID_BOT = 14336
ID_TICKET_SETOR = 4

class AtendimentoIn(BaseModel):
    id_login: int = Field(description="ID de login do cliente.")
    id_assunto: int = Field(description="ID do assunto do atendimento.")
    id_cliente: int = Field(description="ID do cliente.")
    menssagem: str = Field(description="Mensagem descritiva.")
    origem_endereco: Optional[OrigemEnderecoCod] = Field(default="L", description="Origem de endereço.")
    tipo: Optional[TipoCod] = Field(default="C", description="Tipo do atendimento.")
    titulo: str = Field(description="Título do atendimento.")
    prioridade: Optional[PrioridadeCod] = Field(default="M", description="Pioridade do atendimento.")
    su_status: Optional[SuStatusCod] = Field(default="N", description="Status do atendimento.")
    id_ticket_setor: Optional[int] =  Field(default=ID_TICKET_SETOR, description="Setor do atendimento.")
    id_contrato: int = Field(description="ID de contrato do cliente.")
    id_responsavel_tecnico: Optional[int] = Field(default=ID_BOT, description="ID do responsável técnico.")

class Atendimento(BaseModel):
    id: int = Field(description="ID do atendimento.")
    id_assunto: int = Field(description="ID do assunto do atendimento.")
    status: StatusAtendimentoRot = Field(description="Status do atendimento.")
    mensagem: str = Field(max_length=999, description="Mensagem descritiva.")
    titulo: str = Field(max_length=200, description="Título do atendimento.")
    data_criacao: str = Field(description="Data de criação do atendimento.")

class AtendimentoOut(BaseModel):
    data: List[Atendimento]
    meta: Meta
    links: Links