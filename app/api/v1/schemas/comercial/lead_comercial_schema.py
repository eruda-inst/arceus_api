import re
from app.api.v1 import utils
from pydantic import BaseModel, Field, PositiveInt, EmailStr, field_serializer


class LeadOut(BaseModel):
    ativo: utils.enums.codigos.lead_cod_enum.AtivoCod = Field(
        max_length=1,
        description="Indica se o lead esta ativo (S para Sim, N para Não).",
        examples=[utils.enums.codigos.lead_cod_enum.AtivoCod.SIM],
    )
    principal: utils.enums.codigos.lead_cod_enum.PrincipalCod = Field(
        max_length=1,
        description="Indica se o lead é o principal (S para Sim, N para Não).",
        examples=[utils.enums.codigos.lead_cod_enum.PrincipalCod.SIM],
    )
    lead: utils.enums.codigos.lead_cod_enum.LeadCod = Field(
        description="ID do tipo de contato.",
        examples=[utils.enums.codigos.lead_cod_enum.LeadCod.SIM],
    )
    tipo_pessoa: str = Field(
        max_length=1,
        examples=[utils.enums.codigos.TipoPessoaCod.FISICA],
        description="Tipo de pessoa (F para Física, J para Jurídica, E para Estrangeiro).",
    )
    nome: str = Field(
        max_length=200,
        description="Nome do potencial cliente associado ao lead.",
        examples=["João"],
    )
    data_nascimento: str = Field(
        max_length=20,
        description="Data de nascimento do cliente.",
        examples=["01/01/2000"],
    )
    id_filial: PositiveInt = Field(
        description="ID da filial associada ao lead.", examples=[1]
    )
    fone_celular: str = Field(
        max_length=20,
        description="Número do celular do potencial cliente associado ao lead.",
        examples=["(12) 93456-7890"],
    )
    fone_whatsapp: str = Field(
        max_length=20,
        description="Número do celular do potencial cliente associado ao lead.",
        examples=["(12) 93456-7890"],
    )
    cep: str = Field(
        min_length=9,
        max_length=9,
        description="CEP do potencial cliente associado ao lead.",
        examples=["12345-678"],
    )
    endereco: str = Field(
        max_length=200,
        description="Endereço do potencial cliente associado ao lead.",
        examples=["Rua do Lead"],
    )
    numero: str | PositiveInt = Field(
        default="S/N",
        description="Número da casa do potencial cliente associado ao lead.",
        examples=["123"],
    )
    bairro: str = Field(
        max_length=200,
        description="Bairro do potencial cliente associado ao lead.",
        examples=["Bairro do Lead"],
    )
    uf: PositiveInt = Field(description="UF do potencial cliente.")
    cnpj_cpf: str = Field(
        max_length=30,
        description="CNPJ ou CPF do potencial cliente associado ao lead.",
        examples=["123.456.789-00"],
    )
    cidade: PositiveInt = Field(
        description="Nome da cidade associada ao lead.",
        examples=["Jacobina"],
    )
    id_vd_contrato: PositiveInt = Field(
        description="Nome do plano de contrato associado ao lead.",
        examples=["Nome do plano de contrato"],
    )
    id_responsavel: PositiveInt = Field(
        description="ID do responsável técnico associado ao lead.",
        examples=[utils.Default.ID_RESPONSAVEL_ARCEUS],
    )
    email: EmailStr = Field(
        description="E-mail do potencial cliente associado ao lead.",
        examples=["exemplo@examplo.com"],
    )
    id_candidato_tipo: PositiveInt = Field(
        description="Canal de venda.",
        examples=["Canal de venda"],
    )
    obs: str = Field(
        description="Observação associada ao lead.",
        examples=["Observação associada ao lead"],
    )

    @field_serializer("ativo")
    def formatar_ativo(self, v):
        v = str.upper(v)
        rot = utils.AtivoRot.SIM if v == utils.AtivoCod.SIM else utils.AtivoRot.NAO
        return rot

    @field_serializer("principal")
    def formatar_principal(self, v):
        v = str.upper(v)
        rot = (
            utils.PrincipalRot.SIM
            if v == utils.PrincipalCod.SIM
            else utils.PrincipalRot.NAO
        )
        return rot

    @field_serializer("tipo_pessoa")
    def formatar_tipo_pessoa(self, v):
        v = str.upper(v)
        rot = utils.TipoPessoaRot.FISICA
        rot = utils.TipoPessoaRot.JURIDICA if v == utils.TipoPessoaCod.JURIDICA else rot
        rot = (
            utils.TipoPessoaRot.ESTRANGEIRO
            if v == utils.TipoPessoaCod.ESTRANGEIRO
            else rot
        )
        return rot

    @field_serializer("lead")
    def formatar_lead(self, v):
        v = str.upper(v)
        rot = utils.LeadRot.SIM if v == utils.AtivoCod.SIM else utils.LeadRot.NAO
        return rot


class LeadUpdate(BaseModel):
    ativo: utils.enums.codigos.lead_cod_enum.AtivoCod | None = Field(
        default=None,
        max_length=1,
        description="Indica se o lead esta ativo (S para Sim, N para Não).",
        examples=[utils.enums.codigos.lead_cod_enum.AtivoCod.SIM],
    )
    principal: utils.enums.codigos.lead_cod_enum.PrincipalCod | None = Field(
        default=None,
        max_length=1,
        description="Indica se o lead é o principal (S para Sim, N para Não).",
        examples=[utils.enums.codigos.lead_cod_enum.PrincipalCod.SIM],
    )
    lead: utils.enums.codigos.lead_cod_enum.LeadCod | None = Field(
        default=None,
        description="ID do tipo de contato.",
        examples=[utils.enums.codigos.lead_cod_enum.LeadCod.SIM],
    )
    tipo_pessoa: str | None = Field(
        default=None,
        examples=[utils.enums.codigos.TipoPessoaCod.FISICA],
        description="Tipo de pessoa (F para Física, J para Jurídica, E para Estrangeiro).",
    )
    nome: str | None = Field(
        default=None,
        max_length=200,
        description="Nome do potencial cliente associado ao lead.",
        examples=["João"],
    )
    data_nascimento: str | None = Field(
        default=None,
        max_length=20,
        description="Data de nascimento do cliente.",
        examples=["01/01/2000"],
    )
    id_filial: PositiveInt | None = Field(
        default=None, description="ID da filial associada ao lead.", examples=[1]
    )
    fone_celular: str | None = Field(
        default=None,
        max_length=20,
        description="Número do celular do potencial cliente associado ao lead.",
        examples=["(12) 93456-7890"],
    )
    fone_whatsapp: str | None = Field(
        default=None,
        max_length=20,
        description="Número do celular do potencial cliente associado ao lead.",
        examples=["(12) 93456-7890"],
    )
    cep: str | None = Field(
        default=None,
        min_length=8,
        max_length=9,
        description="CEP do potencial cliente associado ao lead.",
        examples=["12345-678"],
    )
    endereco: str | None = Field(
        default=None,
        max_length=200,
        description="Endereço do potencial cliente associado ao lead.",
        examples=["Rua do Lead"],
    )
    numero: str | PositiveInt | None = Field(
        default=None,
        description="Número da casa do potencial cliente associado ao lead.",
        examples=["123"],
    )
    bairro: str | None = Field(
        default=None,
        max_length=200,
        description="Bairro do potencial cliente associado ao lead.",
        examples=["Bairro do Lead"],
    )
    uf: PositiveInt | None = Field(default=None, description="UF do potencial cliente.")
    cnpj_cpf: str | None = Field(
        default=None,
        max_length=30,
        description="CNPJ ou CPF do potencial cliente associado ao lead.",
        examples=["123.456.789-00"],
    )
    cidade: PositiveInt | None = Field(
        default=None,
        description="ID da cidade associada ao lead.",
        examples=[utils.Default.ID_CIDADE_JACOBINA],
    )
    id_vd_contrato: PositiveInt | None = Field(
        default=None,
        description="ID do plano de contrato associado ao lead.",
        examples=[utils.Default.ID_VD_CONTRATO],
    )
    id_responsavel: PositiveInt | None = Field(
        default=None,
        description="ID do responsável técnico associado ao lead.",
        examples=[utils.Default.ID_RESPONSAVEL_ARCEUS],
    )
    email: EmailStr | None = Field(
        default=None,
        description="Email do potencial cliente associado ao lead.",
        examples=["exemplo@examplo.com"],
    )
    id_candidato_tipo: PositiveInt | None = Field(
        default=None,
        description="Canal de venda",
        examples=[utils.Default.ID_CANAL_VENDA],
    )
    obs: str | None = Field(
        default=None,
        description="Observação associada ao lead.",
        examples=["Observação associada ao lead."],
    )

    @field_serializer("cep")
    def formatar_cep(self, v):
        primeira_parte = v[:5]
        segunda_parte = v[5:]
        cep_pattern = r"^\d{5}-\d{3}$"
        if re.match(pattern=cep_pattern, string=v):
            return v
        return f"{primeira_parte}-{segunda_parte}"

    @field_serializer("ativo")
    def formatar_ativo(self, v):
        return str.upper(v)

    @field_serializer("principal")
    def formatar_principal(self, v):
        return str.upper(v)

    @field_serializer("tipo_pessoa")
    def formatar_tipo_pessoa(self, v):
        return str.upper(v)

    @field_serializer("lead")
    def formatar_lead(self, v):
        return str.upper(v)


class LeadIn(BaseModel):
    ativo: utils.enums.codigos.lead_cod_enum.AtivoCod | None = Field(
        default=utils.enums.codigos.lead_cod_enum.AtivoCod.SIM,
        max_length=1,
        description="Indica se o lead esta ativo (S para Sim, N para Não).",
        examples=[utils.enums.codigos.lead_cod_enum.AtivoCod.SIM],
    )
    principal: utils.enums.codigos.lead_cod_enum.PrincipalCod | None = Field(
        default=utils.enums.codigos.lead_cod_enum.PrincipalCod.SIM,
        max_length=1,
        description="Indica se o lead é o principal (S para Sim, N para Não).",
        examples=[utils.enums.codigos.lead_cod_enum.PrincipalCod.SIM],
    )
    lead: utils.enums.codigos.lead_cod_enum.LeadCod | None = Field(
        default=utils.enums.codigos.lead_cod_enum.LeadCod.SIM,
        description="ID do tipo de contato.",
        examples=[utils.enums.codigos.lead_cod_enum.LeadCod.SIM],
    )
    tipo_pessoa: str | None = Field(
        default=utils.enums.codigos.TipoPessoaCod.FISICA,
        examples=[utils.enums.codigos.TipoPessoaCod.FISICA],
        description="Tipo de pessoa (F para Física, J para Jurídica, E para Estrangeiro).",
    )
    # Campo obrigatório para a API do IXC: nome
    nome: str = Field(
        max_length=200,
        description="Nome do potencial cliente associado ao lead.",
        examples=["João"],
    )
    # Formato de data aceito pel API do IXC: dd/mm/aaaa
    data_nascimento: str = Field(
        max_length=20,
        description="Data de nascimento do cliente.",
        examples=["01/01/2000"],
    )
    # Campo obrigatório para a API do IXC: id_filial
    id_filial: PositiveInt | None = Field(
        default=1, description="ID da filial associada ao lead.", examples=[1]
    )
    fone_celular: str = Field(
        max_length=20,
        description="Número do celular do potencial cliente associado ao lead.",
        examples=["(12) 93456-7890"],
    )
    # Campo obrigatório para a API do IXC: fone_whatsapp (ou qualquer outro telefone)
    fone_whatsapp: str = Field(
        max_length=20,
        description="Número do celular do potencial cliente associado ao lead.",
        examples=["(12) 93456-7890"],
    )
    cep: str | None = Field(
        default="44700-000",
        min_length=8,
        max_length=9,
        description="CEP do potencial cliente associado ao lead.",
        examples=["12345-678"],
    )
    endereco: str = Field(
        max_length=200,
        description="Endereço do potencial cliente associado ao lead.",
        examples=["Rua do Lead"],
    )
    numero: str | PositiveInt | None = Field(
        default="S/N",
        description="Número da casa do potencial cliente associado ao lead.",
        examples=["123"],
    )
    bairro: str = Field(
        max_length=200,
        description="Bairro do potencial cliente associado ao lead.",
        examples=["Bairro do Lead"],
    )
    uf: PositiveInt | None = Field(default=10, description="UF do potencial cliente.")
    cnpj_cpf: str = Field(
        max_length=30,
        description="CNPJ ou CPF do potencial cliente associado ao lead.",
        examples=["123.456.789-00"],
    )
    cidade: PositiveInt | None = Field(
        utils.Default.ID_CIDADE_JACOBINA,
        description="ID da cidade associada ao lead.",
        examples=[utils.Default.ID_CIDADE_JACOBINA],
    )
    id_vd_contrato: PositiveInt | None = Field(
        utils.Default.ID_VD_CONTRATO,
        description="ID do plano de contrato associado ao lead.",
        examples=[utils.Default.ID_VD_CONTRATO],
    )
    id_responsavel: PositiveInt | None = Field(
        utils.Default.ID_RESPONSAVEL_ARCEUS,
        description="ID do responsável técnico associado ao lead.",
        examples=[utils.Default.ID_RESPONSAVEL_ARCEUS],
    )
    email: EmailStr = Field(
        description="Email do potencial cliente associado ao lead.",
        examples=["exemplo@examplo.com"],
    )
    id_candidato_tipo: PositiveInt | None = Field(
        default=utils.Default.ID_CANAL_VENDA,
        description="Canal de venda",
        examples=[utils.Default.ID_CANAL_VENDA],
    )
    obs: str | None = Field(
        default=None,
        description="Observação associada ao lead.",
        examples=["Observação associada ao lead."],
    )

    @field_serializer("cep")
    def formatar_cep(self, v):
        primeira_parte = v[:5]
        segunda_parte = v[5:]
        cep_pattern = r"^\d{5}-\d{3}$"
        if re.match(pattern=cep_pattern, string=v):
            return v
        return f"{primeira_parte}-{segunda_parte}"

    @field_serializer("ativo")
    def formatar_ativo(self, v):
        return str.upper(v)

    @field_serializer("principal")
    def formatar_principal(self, v):
        return str.upper(v)

    @field_serializer("tipo_pessoa")
    def formatar_tipo_pessoa(self, v):
        return str.upper(v)

    @field_serializer("lead")
    def formatar_lead(self, v):
        return str.upper(v)


class LeadCreate(BaseModel):
    id: PositiveInt = Field(description="ID do lead criado.", examples=[12345])
