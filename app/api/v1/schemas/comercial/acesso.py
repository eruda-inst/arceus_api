from app.api.v1 import utils
from pydantic import BaseModel, Field


class StatusAcesso(BaseModel):
    status_acesso: utils.StatusAcessoRot = Field(
        description="Status de acesso.", examples=[utils.StatusAcessoRot.DESATIVADO]
    )


class StatusAcessoOut(BaseModel):
    data: StatusAcesso = Field()
