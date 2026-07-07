from .. import utils
from pydantic import (
    Field,
    EmailStr,
    BaseModel,
    PositiveInt,
    NonNegativeInt,
    field_serializer,
)


class LeadOut(BaseModel):
    id: NonNegativeInt = Field(description="ID do lead.", examples=[1])
    ativo: utils.AtivoCod = Field(
        description="Indica se o lead está ativo.",
        min_length=1,  # S
        max_length=3,  # Sim
        examples=[utils.AtivoRot.SIM],
    )
    principal: utils.PrincipalCod = Field(
        description="Indica se o lead é principal.",
        min_length=1,  # S
        max_length=3,  # Sim
        examples=[utils.PrincipalRot.SIM],
    )
    lead: utils.LeadCod = Field(
        description="Indica se é lead.",
        min_length=1,  # S
        max_length=3,  # Sim
        examples=[utils.LeadRot.SIM],
    )
    tipo_pessoa: utils.TipoPessoaCod = Field(
        description="Tipo de pessoa.", examples=[utils.TipoPessoaRot.FISICA]
    )
    nome: str = Field(description="Nome do cliente.", examples=["João"])
    data_nascimento: str = Field(
        description="Data de nascimento do cliente.",
        # Não pode haver isto, pois o IXC é quebrado
        # min_length=10,  # YYYY-MM-AA
        # max_length=10,  # YYYY-MM-AA
        examples=["dd/mm/aaaa"],
    )
    id_filial: NonNegativeInt = Field(
        description="ID da filial.", examples=[utils.Default.ID_FILIAL]
    )
    fone_celular: str = Field(
        description="Celular do cliente.",
        min_length=11,  # 12934567890
        max_length=15,  # (12) 93456-7890
        examples=["(12) 93456-7890"],
    )
    fone_whatsapp: str = Field(
        description="Celular do cliente.",
        min_length=11,  # 12934567890
        max_length=15,  # (12) 93456-7890
        examples=["(12) 93456-7890"],
    )
    cep: str = Field(
        min_length=8,  # 12345678
        max_length=9,  # 12345-678
        description="CEP do cliente.",
        examples=["12345-678"],
    )
    endereco: str = Field(description="Rua do cliente.", examples=["Rua do cliente"])
    numero: str | PositiveInt = Field(
        default="S/N", description="Número da casa do cliente.", examples=[42]
    )
    bairro: str = Field(
        description="Bairro do cliente.", examples=["Bairro do cliente"]
    )
    uf: PositiveInt = Field(description="ID da UF.", examples=[utils.Default.ID_UF])
    cnpj_cpf: str = Field(
        description="CNPJ ou CPF do cliente.",
        min_length=11,  # 12345678900
        max_length=18,  # 12.345.678/0001-90
        examples=["123.456.789-00"],
    )
    cidade: PositiveInt = Field(
        description="ID da cidade.", examples=[utils.Default.ID_CIDADE_JAC]
    )
    id_vd_contrato: NonNegativeInt = Field(description="ID do Plano.", examples=[42])
    id_responsavel: NonNegativeInt = Field(
        description="ID do responsável técnico.",
        examples=[utils.Default.ID_RESPONSAVEL_ARCEUS],
    )
    email: EmailStr = Field(
        description="E-mail do cliente.", examples=["email@email.com"]
    )
    id_candidato_tipo: NonNegativeInt = Field(
        description="ID do canal de venda.", examples=[42]
    )
    obs: str = Field(description="Observação do lead.", examples=["Observação do lead"])

    @field_serializer("ativo")
    def serialize_ativo(self, v: utils.AtivoCod) -> utils.AtivoRot:
        cod = utils.AtivoCod
        rot = utils.AtivoRot

        mapping = {cod.SIM: rot.SIM, cod.NAO: rot.NAO}

        return mapping[v]

    @field_serializer("principal")
    def serialize_principal(self, v: utils.PrincipalCod) -> utils.PrincipalRot:
        cod = utils.PrincipalCod
        rot = utils.PrincipalRot

        mapping = {cod.SIM: rot.SIM, cod.NAO: rot.NAO}

        return mapping[v]

    @field_serializer("lead")
    def serialize_lead(self, v: utils.LeadCod) -> utils.LeadRot:
        cod = utils.LeadCod
        rot = utils.LeadRot

        mapping = {cod.SIM: rot.SIM, cod.NAO: rot.NAO}

        return mapping[v]

    @field_serializer("tipo_pessoa")
    def serialize_tipo_pessoa(self, v: utils.TipoPessoaCod) -> utils.TipoPessoaRot:
        cod = utils.TipoPessoaCod
        rot = utils.TipoPessoaRot

        mapping = {
            cod.FISICA: rot.FISICA,
            cod.JURIDICA: rot.JURIDICA,
            cod.ESTRANGEIRO: rot.ESTRANGEIRO,
        }

        return mapping[v]

    @field_serializer("data_nascimento")
    def serialize_data_nascimento(self, v: str) -> str:
        return utils.Formatter.data(data=v)

    @field_serializer("fone_celular")
    def serialize_fone_celular(self, v: str) -> str:
        return utils.Formatter.cell(cell=v)

    @field_serializer("fone_whatsapp")
    def serialize_fone_whatsapp(self, v: str) -> str:
        return utils.Formatter.cell(cell=v)

    @field_serializer("cep")
    def serialize_cep(self, v: str) -> str:
        return utils.Formatter.cep(cep=v)

    @field_serializer("cnpj_cpf")
    def serialize_cnpj_cpf(self, v: str) -> str:
        return utils.Formatter.cnpj_cpf(cnpj_cpf=v)


class LeadUpdate(BaseModel):
    ativo: utils.AtivoCod | None = Field(
        default=None,
        min_length=1,  # S
        max_length=1,  # S
        description="Indica se o lead está ativo.",
        examples=[utils.AtivoCod.SIM],
    )
    principal: utils.PrincipalCod | None = Field(
        default=None,
        min_length=1,  # S
        max_length=1,  # S
        description="Indica se o lead é principal.",
        examples=[utils.PrincipalCod.SIM],
    )
    lead: utils.LeadCod | None = Field(
        default=None,
        min_length=1,  # S
        max_length=1,  # S
        description="Indica se é lead.",
        examples=[utils.LeadCod.SIM],
    )
    tipo_pessoa: utils.TipoPessoaCod | None = Field(
        default=None,
        min_length=1,  # F
        max_length=1,  # F
        description="Tipo de pessoa.",
        examples=[utils.TipoPessoaCod.FISICA],
    )
    nome: str | None = Field(
        default=None, description="Nome do cliente.", examples=["Nome do Cliente"]
    )
    data_nascimento: str | None = Field(
        default=None,
        min_length=10,  # dd/mm/aaaa
        max_length=10,  # dd/mm/aaaa
        description="Data de nascimento.",
        examples=["dd/mm/aaaa"],
    )
    id_filial: NonNegativeInt | None = Field(
        default=None, description="ID da filial.", examples=[utils.Default.ID_FILIAL]
    )
    fone_celular: str | None = Field(
        default=None,
        min_length=11,  # 12934567890
        max_length=15,  # (12) 93456-7890
        description="Celular do cliente.",
        examples=["(12) 93456-7890"],
    )
    fone_whatsapp: str | None = Field(
        default=None,
        min_length=11,  # 12934567890
        max_length=15,  # (12) 93456-7890
        description="Celular do cliente.",
        examples=["(12) 93456-7890"],
    )
    cep: str | None = Field(
        default=None,
        min_length=8,  # 12345678
        max_length=9,  # 12345-678
        description="CEP do cliente.",
        examples=["12345-678"],
    )
    endereco: str | None = Field(
        default=None, description="Rua do cliente.", examples=["Rua do cliente"]
    )
    numero: str | PositiveInt | None = Field(
        default=None, description="Número da casa do cliente.", examples=[42]
    )
    bairro: str | None = Field(
        default=None, description="Bairro do cliente.", examples=["Bairro do cliente"]
    )
    uf: PositiveInt | None = Field(
        default=None, description="ID da UF.", examples=[utils.Default.ID_UF]
    )
    cnpj_cpf: str | None = Field(
        default=None,
        min_length=11,  # 12345678900
        max_length=18,  # 12.345.678/0001-90
        description="CNPJ ou CPF do cliente.",
        examples=["123.456.789-00"],
    )
    cidade: PositiveInt | None = Field(
        default=None,
        description="ID da cidade.",
        examples=[utils.Default.ID_CIDADE_JAC],
    )
    id_vd_contrato: NonNegativeInt | None = Field(
        default=None,
        description="ID do plano.",
        examples=[utils.Default.ID_VD_CONTRATO],
    )
    id_responsavel: NonNegativeInt | None = Field(
        default=None,
        description="ID do responsável técnico.",
        examples=[utils.Default.ID_RESPONSAVEL_ARCEUS],
    )
    email: EmailStr | None = Field(
        default=None, description="E-mail do cliente.", examples=["email@email.com"]
    )
    id_candidato_tipo: NonNegativeInt | None = Field(
        default=None,
        description="ID do canal de venda",
        examples=[utils.Default.ID_CANAL_VENDA],
    )
    obs: str | None = Field(
        default=None,
        description="Observação do lead.",
        examples=["Observação do lead."],
    )

    @field_serializer("data_nascimento")
    def serialize_data_nascimento(self, v: str) -> str:
        return utils.Formatter.data(data=v)

    @field_serializer("fone_celular")
    def serialize_fone_celular(self, v: str) -> str:
        return utils.Formatter.cell(cell=v)

    @field_serializer("fone_whatsapp")
    def serialize_fone_whatsapp(self, v: str) -> str:
        return utils.Formatter.cell(cell=v)

    @field_serializer("cep")
    def serialize_cep(self, v: str) -> str:
        return utils.Formatter.cep(cep=v)

    @field_serializer("cnpj_cpf")
    def serialize_cnpj_cpf(self, v: str) -> str:
        return utils.Formatter.cnpj_cpf(cnpj_cpf=v)


class LeadIn(BaseModel):
    ativo: utils.AtivoCod | None = Field(
        default=utils.AtivoCod.SIM,
        min_length=1,  # S
        max_length=1,  # S
        description="Indica se o lead está ativo.",
        examples=[utils.AtivoCod.SIM],
    )
    principal: utils.PrincipalCod | None = Field(
        default=utils.PrincipalCod.SIM,
        min_length=1,  # S
        max_length=1,  # S
        description="Indica se o lead é principal.",
        examples=[utils.PrincipalCod.SIM],
    )
    lead: utils.LeadCod | None = Field(
        default=utils.LeadCod.SIM,
        min_length=1,  # S
        max_length=1,  # S
        description="Indica se é lead.",
        examples=[utils.LeadCod.SIM],
    )
    tipo_pessoa: str | None = Field(
        default=utils.TipoPessoaCod.FISICA,
        min_length=1,  # F
        max_length=1,  # F
        examples=[utils.TipoPessoaCod.FISICA],
        description="Tipo de pessoa.",
    )
    nome: str = Field(
        description="Nome do cliente.",
        examples=["Nome do Cliente"],
    )
    data_nascimento: str = Field(
        description="Data de nascimento.",
        # Não pode haver isto, pois o IXC é quebrado
        # min_length=10,  # YYYY-MM-AA
        # max_length=10,  # YYYY-MM-AA
        examples=["dd/mm/aaaa"],
    )
    id_filial: NonNegativeInt | None = Field(
        default=utils.Default.ID_FILIAL,
        description="ID da filial.",
        examples=[utils.Default.ID_FILIAL],
    )
    fone_celular: str = Field(
        description="Celular do cliente.",
        min_length=11,  # 12934567890
        max_length=15,  # (12) 93456-7890
        examples=["(12) 93456-7890"],
    )
    fone_whatsapp: str = Field(
        description="Celular do cliente.",
        min_length=11,  # 12934567890
        max_length=15,  # (12) 93456-7890
        examples=["(12) 93456-7890"],
    )
    cep: str | None = Field(
        default="44700-000",
        min_length=8,  # 12345678
        max_length=9,  # 12345-678
        description="CEP do cliente.",
        examples=["12345-678"],
    )
    endereco: str = Field(description="Rua do cliente.", examples=["Rua do cliente"])
    numero: str | PositiveInt | None = Field(
        default="S/N", description="Número da casa do cliente.", examples=[42]
    )
    bairro: str = Field(
        description="Bairro do cliente.", examples=["Bairro do cliente"]
    )
    uf: PositiveInt | None = Field(
        default=utils.Default.ID_UF,
        description="ID da UF.",
        examples=[utils.Default.ID_UF],
    )
    cnpj_cpf: str = Field(
        description="CNPJ ou CPF do cliente.",
        min_length=11,  # 12345678900
        max_length=18,  # 12.345.678/0001-90
        examples=["123.456.789-00"],
    )
    cidade: PositiveInt | None = Field(
        default=utils.Default.ID_CIDADE_JAC,
        description="ID da cidade.",
        examples=[utils.Default.ID_CIDADE_JAC],
    )
    id_vd_contrato: NonNegativeInt | None = Field(
        default=utils.Default.ID_VD_CONTRATO,
        description="ID do plano.",
        examples=[utils.Default.ID_VD_CONTRATO],
    )
    id_responsavel: NonNegativeInt | None = Field(
        default=utils.Default.ID_RESPONSAVEL_ARCEUS,
        description="ID do responsável técnico.",
        examples=[utils.Default.ID_RESPONSAVEL_ARCEUS],
    )
    email: EmailStr = Field(
        description="E-mail do cliente.", examples=["email@email.com"]
    )
    id_candidato_tipo: NonNegativeInt | None = Field(
        default=utils.Default.ID_CANAL_VENDA,
        description="Canal de venda.",
        examples=[utils.Default.ID_CANAL_VENDA],
    )
    obs: str | None = Field(
        default=None,
        description="Observação do lead.",
        examples=["Observação do lead."],
    )

    @field_serializer("cnpj_cpf")
    def serialize_cnpj_cpf(self, v: str) -> str:
        return utils.Formatter.cnpj_cpf(cnpj_cpf=v)

    @field_serializer("fone_whatsapp")
    def serialize_fone_whatsapp(self, v: str) -> str:
        return utils.Formatter.cell(cell=v)

    @field_serializer("fone_celular")
    def serialize_fone_celular(self, v: str) -> str:
        return utils.Formatter.cell(cell=v)

    @field_serializer("cep")
    def serialize_cep(self, v: str) -> str:
        return utils.Formatter.cep(cep=v)

    @field_serializer("data_nascimento")
    def serialize_data_nascimento(self, v: str) -> str:
        return utils.Formatter.data(data=v)


class LeadCreate(BaseModel):
    id: NonNegativeInt = Field(description="ID do lead criado.", examples=[42])
