from pydantic import BaseModel, Field
from app.api.v1.utils import StatusAcessoRot


class StatusAcesso(BaseModel):
    status_acesso: StatusAcessoRot = Field(description="Status de acesso.")


class StatusAcessoOut(BaseModel):
    data: StatusAcesso
