from app.api.v1 import utils
from pydantic import BaseModel, Field


class StatusAcesso(BaseModel):
    status_acesso: utils.StatusAcessoRot = Field(description="Status de acesso.")

    model_config = {
        "json_schema_extra": {
            "examples": [{"status_acesso": utils.StatusAcessoRot.DESATIVADO}]
        }
    }


class StatusAcessoOut(BaseModel):
    data: StatusAcesso

    model_config = {
        "json_schema_extra": {
            "examples": [{"status_acesso": utils.StatusAcessoRot.DESATIVADO}]
        }
    }
