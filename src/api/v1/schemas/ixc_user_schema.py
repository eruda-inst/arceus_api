from pydantic import BaseModel, EmailStr, Field, PositiveInt, field_serializer

from .. import utils


class IXCUserOut(BaseModel):
    id: PositiveInt = Field(description="ID do usuário", examples=[1])
    nome: str = Field(description="Nome do usuário", examples=["Nome do usuário"])
    email: EmailStr = Field(
        description="E-mail do usuário", examples=["exemplo@exemplo"]
    )
    status: utils.IXCUserStatusCod | None = Field(
        default=utils.IXCUserStatusCod.ATIVO,
        description="Status do usuário",
        examples=[utils.IXCUserStatusLabel.ATIVO],
    )
    tipo_acesso: utils.IXCUserAccessTypeCod | None = Field(
        default=utils.IXCUserAccessTypeCod.AMBOS,
        description="Tipo de acesso do usuário",
        examples=[utils.IXCUserAccessTypeLabel.AMBOS],
    )

    @field_serializer("status")
    def serialize_status(self, v: utils.IXCUserStatusCod) -> utils.IXCUserStatusLabel:
        map = {
            utils.IXCUserStatusCod.ATIVO: utils.IXCUserStatusLabel.ATIVO,
            utils.IXCUserStatusCod.INATIVO: utils.IXCUserStatusLabel.INATIVO,
        }
        return map[v]

    @field_serializer("tipo_acesso")
    def serialize_tipo_acesso(
        self, v: utils.IXCUserAccessTypeCod
    ) -> utils.IXCUserAccessTypeLabel:
        map = {
            utils.IXCUserAccessTypeCod.AMBOS: utils.IXCUserAccessTypeLabel.AMBOS,
            utils.IXCUserAccessTypeCod.MOBILE: utils.IXCUserAccessTypeLabel.MOBILE,
            utils.IXCUserAccessTypeCod.WEB: utils.IXCUserAccessTypeLabel.WEB,
        }
        return map[v]
