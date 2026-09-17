from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    NonNegativeInt,
    PositiveInt,
    field_serializer,
)

from .. import utils


class LeadOutSchema(BaseModel):
    id: NonNegativeInt = Field(description="ID do lead", examples=[1])
    ativo: utils.YesNoCode = Field(
        description="Indica se o lead está ativo",
        min_length=1,  # S
        max_length=3,  # Sim
        examples=[utils.YesNoLabel.NO],
    )
    principal: utils.YesNoCode = Field(
        description="Indica se o lead é principal",
        min_length=1,  # S
        max_length=3,  # Sim
        examples=[utils.YesNoLabel.NO],
    )
    lead: utils.YesNoCode = Field(
        description="Indica se é lead",
        min_length=1,  # S
        max_length=3,  # Sim
        examples=[utils.YesNoLabel.NO],
    )
    tipo_pessoa: utils.PersonTypeCode = Field(
        description="Tipo de pessoa", examples=[utils.PersonTypeLabel.LEGAL_ENTITY]
    )
    nome: str = Field(description="Nome do cliente", examples=["João"])
    data_nascimento: str = Field(
        description="Data de nascimento do cliente",
        # Não pode haver isto, pois o IXC é quebrado
        # min_length=10,  # DD/MM/AAAA
        # max_length=10,  # DD/MM/AAAA
        examples=["DD/MM/AAAA"],
    )
    id_filial: NonNegativeInt = Field(
        description="ID da filial", examples=[utils.Default.ID_FILIAL]
    )
    fone_celular: str = Field(
        description="Celular do cliente",
        min_length=11,  # 12934567890
        max_length=15,  # (12) 93456-7890
        examples=["(12) 93456-7890"],
    )
    fone_whatsapp: str = Field(
        description="Celular do cliente",
        min_length=11,  # 12934567890
        max_length=15,  # (12) 93456-7890
        examples=["(12) 93456-7890"],
    )
    cep: str = Field(
        min_length=8,  # 12345678
        max_length=9,  # 12345-678
        description="CEP do cliente",
        examples=["12345-678"],
    )
    endereco: str = Field(description="Rua do cliente", examples=["Rua do cliente"])
    numero: str | PositiveInt = Field(
        default="S/N", description="Número da casa do cliente", examples=[42]
    )
    bairro: str = Field(description="Bairro do cliente", examples=["Bairro do cliente"])
    uf: PositiveInt = Field(description="ID da UF", examples=[utils.Default.ID_UF])
    cnpj_cpf: str = Field(
        description="CNPJ ou CPF do cliente",
        min_length=11,  # 12345678900
        max_length=18,  # 12.345.678/0001-90
        examples=["123.456.789-00"],
    )
    cidade: PositiveInt = Field(
        description="ID da cidade", examples=[utils.Default.ID_CIDADE_JAC]
    )
    id_vd_contrato: NonNegativeInt = Field(description="ID do Plano.", examples=[42])
    id_responsavel: NonNegativeInt = Field(
        description="ID do responsável técnico",
        examples=[utils.Default.ID_RESPONSAVEL_ARCEUS],
    )
    email: EmailStr = Field(
        description="E-mail do cliente", examples=["email@email.com"]
    )
    id_candidato_tipo: NonNegativeInt = Field(
        description="ID do canal de venda", examples=[42]
    )
    obs: str = Field(description="Observação do lead", examples=["Observação do lead"])

    @field_serializer("ativo", "principal", "lead")
    def serialize_ativo(self, v: utils.YesNoCode) -> utils.YesNoLabel:
        cod = utils.YesNoCode
        rot = utils.YesNoLabel

        mapping = {cod.YES: rot.YES, cod.NO: rot.NO}

        return mapping[v]

    @field_serializer("tipo_pessoa")
    def serialize_tipo_pessoa(self, v: utils.PersonTypeCode) -> utils.PersonTypeLabel:
        cod = utils.PersonTypeCode
        rot = utils.PersonTypeLabel

        mapping = {
            cod.INDIVIDUAL: rot.INDIVIDUAL,
            cod.LEGAL_ENTITY: rot.LEGAL_ENTITY,
            cod.FOREIGN: rot.FOREIGN,
        }

        return mapping[v]

    @field_serializer("data_nascimento")
    def serialize_data_nascimento(self, v: str) -> str:
        return utils.Formatter.date(date=v)

    @field_serializer("fone_celular", "fone_whatsapp")
    def serialize_fone_celular(self, v: str) -> str:
        return utils.Formatter.cell(cell=v)

    @field_serializer("cep")
    def serialize_cep(self, v: str) -> str:
        return utils.Formatter.cep(cep=v)

    @field_serializer("cnpj_cpf")
    def serialize_cnpj_cpf(self, v: str) -> str:
        return utils.Formatter.cnpj_cpf(cnpj_cpf=v)


class LeadUpdateSchema(BaseModel):
    ativo: utils.YesNoCode | None = Field(
        default=None,
        min_length=1,  # S
        max_length=1,  # S
        description="Indica se o lead está ativo",
        examples=[utils.YesNoCode.YES],
    )
    principal: utils.YesNoCode | None = Field(
        default=None,
        min_length=1,  # S
        max_length=1,  # S
        description="Indica se o lead é principal",
        examples=[utils.YesNoCode.YES],
    )
    lead: utils.YesNoCode | None = Field(
        default=None,
        min_length=1,  # S
        max_length=1,  # S
        description="Indica se é lead",
        examples=[utils.YesNoCode.YES],
    )
    tipo_pessoa: utils.PersonTypeCode | None = Field(
        default=None,
        min_length=1,  # F
        max_length=1,  # F
        description="Tipo de pessoa",
        examples=[utils.PersonTypeCode.LEGAL_ENTITY],
    )
    nome: str | None = Field(
        default=None, description="Nome do cliente", examples=["Nome do Cliente"]
    )
    data_nascimento: str | None = Field(
        default=None,
        min_length=10,  # DD/MM/AAAA
        max_length=10,  # DD/MM/AAAA
        description="Data de nascimento",
        examples=["DD/MM/AAAA"],
    )
    id_filial: NonNegativeInt | None = Field(
        default=None, description="ID da filial", examples=[utils.Default.ID_FILIAL]
    )
    fone_celular: str | None = Field(
        default=None,
        min_length=11,  # 12934567890
        max_length=15,  # (12) 93456-7890
        description="Celular do cliente",
        examples=["(12) 93456-7890"],
    )
    fone_whatsapp: str | None = Field(
        default=None,
        min_length=11,  # 12934567890
        max_length=15,  # (12) 93456-7890
        description="Celular do cliente",
        examples=["(12) 93456-7890"],
    )
    cep: str | None = Field(
        default=None,
        min_length=8,  # 12345678
        max_length=9,  # 12345-678
        description="CEP do cliente",
        examples=["12345-678"],
    )
    endereco: str | None = Field(
        default=None, description="Rua do cliente", examples=["Rua do cliente"]
    )
    numero: str | PositiveInt | None = Field(
        default=None, description="Número da casa do cliente", examples=[42]
    )
    bairro: str | None = Field(
        default=None, description="Bairro do cliente", examples=["Bairro do cliente"]
    )
    uf: PositiveInt | None = Field(
        default=None, description="ID da UF", examples=[utils.Default.ID_UF]
    )
    cnpj_cpf: str | None = Field(
        default=None,
        min_length=11,  # 12345678900
        max_length=18,  # 12.345.678/0001-90
        description="CNPJ ou CPF do cliente",
        examples=["123.456.789-00"],
    )
    cidade: PositiveInt | None = Field(
        default=None, description="ID da cidade", examples=[utils.Default.ID_CIDADE_JAC]
    )
    id_vd_contrato: NonNegativeInt | None = Field(
        default=None, description="ID do plano", examples=[utils.Default.ID_VD_CONTRATO]
    )
    id_responsavel: NonNegativeInt | None = Field(
        default=None,
        description="ID do responsável técnico",
        examples=[utils.Default.ID_RESPONSAVEL_ARCEUS],
    )
    email: EmailStr | None = Field(
        default=None, description="E-mail do cliente", examples=["email@email.com"]
    )
    id_candidato_tipo: NonNegativeInt | None = Field(
        default=None,
        description="ID do canal de venda",
        examples=[utils.Default.ID_CANAL_VENDA],
    )
    obs: str | None = Field(
        default=None, description="Observação do lead", examples=["Observação do lead"]
    )

    @field_serializer("data_nascimento")
    def serialize_data_nascimento(self, v: str) -> str:
        return utils.Formatter.date(date=v)

    @field_serializer("fone_celular", "fone_whatsapp")
    def serialize_fone_celular(self, v: str) -> str:
        return utils.Formatter.cell(cell=v)

    @field_serializer("cep")
    def serialize_cep(self, v: str) -> str:
        return utils.Formatter.cep(cep=v)

    @field_serializer("cnpj_cpf")
    def serialize_cnpj_cpf(self, v: str) -> str:
        return utils.Formatter.cnpj_cpf(cnpj_cpf=v)


class LeadInSchema(BaseModel):
    ativo: utils.YesNoCode | None = Field(
        default=utils.YesNoCode.YES,
        min_length=1,  # S
        max_length=1,  # S
        description="Indica se o lead está ativo",
        examples=[utils.YesNoCode.YES],
    )
    principal: utils.YesNoCode | None = Field(
        default=utils.YesNoCode.YES,
        min_length=1,  # S
        max_length=1,  # S
        description="Indica se o lead é principal",
        examples=[utils.YesNoCode.YES],
    )
    lead: utils.YesNoCode | None = Field(
        default=utils.YesNoCode.YES,
        min_length=1,  # S
        max_length=1,  # S
        description="Indica se é lead",
        examples=[utils.YesNoCode.YES],
    )
    tipo_pessoa: str | None = Field(
        default=utils.PersonTypeCode.LEGAL_ENTITY,
        min_length=1,  # F
        max_length=1,  # F
        examples=[utils.PersonTypeCode.LEGAL_ENTITY],
        description="Tipo de pessoa",
    )
    nome: str = Field(description="Nome do cliente", examples=["Nome do Cliente"])
    data_nascimento: str = Field(
        description="Data de nascimento",
        # Não pode haver isto, pois o IXC é quebrado
        # min_length=10,  # DD/MM/AAAA
        # max_length=10,  # DD/MM/AAAA
        examples=["DD/MM/AAAA"],
    )
    id_filial: NonNegativeInt | None = Field(
        default=utils.Default.ID_FILIAL,
        description="ID da filial",
        examples=[utils.Default.ID_FILIAL],
    )
    fone_celular: str = Field(
        description="Celular do cliente",
        min_length=11,  # 12934567890
        max_length=15,  # (12) 93456-7890
        examples=["(12) 93456-7890"],
    )
    fone_whatsapp: str = Field(
        description="Celular do cliente",
        min_length=11,  # 12934567890
        max_length=15,  # (12) 93456-7890
        examples=["(12) 93456-7890"],
    )
    cep: str | None = Field(
        default="44700-000",
        min_length=8,  # 12345678
        max_length=9,  # 12345-678
        description="CEP do cliente",
        examples=["12345-678"],
    )
    endereco: str = Field(description="Rua do cliente", examples=["Rua do cliente"])
    numero: str | PositiveInt | None = Field(
        default="S/N", description="Número da casa do cliente", examples=[42]
    )
    bairro: str = Field(description="Bairro do cliente", examples=["Bairro do cliente"])
    uf: PositiveInt | None = Field(
        default=utils.Default.ID_UF,
        description="ID da UF",
        examples=[utils.Default.ID_UF],
    )
    cnpj_cpf: str = Field(
        description="CNPJ ou CPF do cliente",
        min_length=11,  # 12345678900
        max_length=18,  # 12.345.678/0001-90
        examples=["123.456.789-00"],
    )
    cidade: PositiveInt | None = Field(
        default=utils.Default.ID_CIDADE_JAC,
        description="ID da cidade",
        examples=[utils.Default.ID_CIDADE_JAC],
    )
    id_vd_contrato: NonNegativeInt | None = Field(
        default=utils.Default.ID_VD_CONTRATO,
        description="ID do plano",
        examples=[utils.Default.ID_VD_CONTRATO],
    )
    id_responsavel: NonNegativeInt | None = Field(
        default=utils.Default.ID_RESPONSAVEL_ARCEUS,
        description="ID do responsável técnico",
        examples=[utils.Default.ID_RESPONSAVEL_ARCEUS],
    )
    email: EmailStr = Field(
        description="E-mail do cliente", examples=["email@email.com"]
    )
    id_candidato_tipo: NonNegativeInt | None = Field(
        default=utils.Default.ID_CANAL_VENDA,
        description="Canal de venda",
        examples=[utils.Default.ID_CANAL_VENDA],
    )
    obs: str | None = Field(
        default=None, description="Observação do lead", examples=["Observação do lead"]
    )

    @field_serializer("cnpj_cpf")
    def serialize_cnpj_cpf(self, v: str) -> str:
        return utils.Formatter.cnpj_cpf(cnpj_cpf=v)

    @field_serializer("fone_whatsapp", "fone_celular")
    def serialize_fone_whatsapp(self, v: str) -> str:
        return utils.Formatter.cell(cell=v)

    @field_serializer("cep")
    def serialize_cep(self, v: str) -> str:
        return utils.Formatter.cep(cep=v)

    @field_serializer("data_nascimento")
    def serialize_data_nascimento(self, v: str) -> str:
        return utils.Formatter.date(date=v)


class LeadCreateSchema(BaseModel):
    id: NonNegativeInt = Field(description="ID do lead criado", examples=[42])
