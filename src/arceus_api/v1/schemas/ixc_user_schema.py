"""
Pydantic schemas for IXC user-related responses.
"""

from pydantic import BaseModel, EmailStr, Field, PositiveInt, field_serializer

from .. import utils


class IXCUserOutSchema(BaseModel):
    """
    Response schema for IXC user details.
    """

    id: PositiveInt = Field(description="ID do usuário", examples=[1])
    nome: str = Field(description="Nome do usuário", examples=["Nome do usuário"])
    email: EmailStr = Field(
        description="E-mail do usuário", examples=["exemplo@exemplo"]
    )
    status: utils.IXCUserStatusCode | None = Field(
        default=utils.IXCUserStatusCode.ACTIVE,
        description="Status do usuário",
        examples=[utils.IXCUserStatusLabel.ACTIVE],
    )
    tipo_acesso: utils.IXCUserAccessTypeCode | None = Field(
        default=utils.IXCUserAccessTypeCode.BOTH,
        description="Tipo de acesso do usuário",
        examples=[utils.IXCUserAccessTypeLabel.BOTH],
    )

    @field_serializer("status")
    def serialize_status(self, v: utils.IXCUserStatusCode) -> utils.IXCUserStatusLabel:
        map = {
            utils.IXCUserStatusCode.ACTIVE: utils.IXCUserStatusLabel.ACTIVE,
            utils.IXCUserStatusCode.INACTIVE: utils.IXCUserStatusLabel.INACTIVE,
        }
        return map[v]

    @field_serializer("tipo_acesso")
    def serialize_tipo_acesso(
        self, v: utils.IXCUserAccessTypeCode
    ) -> utils.IXCUserAccessTypeLabel:
        map = {
            utils.IXCUserAccessTypeCode.BOTH: utils.IXCUserAccessTypeLabel.BOTH,
            utils.IXCUserAccessTypeCode.MOBILE: utils.IXCUserAccessTypeLabel.MOBILE,
            utils.IXCUserAccessTypeCode.WEB: utils.IXCUserAccessTypeLabel.WEB,
        }
        return map[v]
