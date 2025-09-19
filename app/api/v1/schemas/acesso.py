from ..utils import StatusAcessoRot
from pydantic import BaseModel, Field


class StatusAcesso(BaseModel):
    status_acesso: StatusAcessoRot = Field(description="Status de acesso.")

class StatusAcessoOut(BaseModel):
    data: StatusAcesso