from app.api.v1 import utils
from typing import Optional, Union
from pydantic import BaseModel, Field, PositiveInt, EmailStr, field_serializer


class LeadIn(BaseModel):
    ativo: Optional[utils.enums.codigos.lead_cod_enum.AtivoCod] = Field(
        default=utils.enums.codigos.lead_cod_enum.AtivoCod.SIM,
        max_length=1,
        description="Indica se o lead esta ativo (S para Sim, N para Não).",
        examples=[utils.enums.codigos.lead_cod_enum.AtivoCod.SIM],
    )
    principal: Optional[utils.enums.codigos.lead_cod_enum.PrincipalCod] = Field(
        default=utils.enums.codigos.lead_cod_enum.PrincipalCod.NAO,
        max_length=1,
        description="Indica se o lead é o principal (S para Sim, N para Não).",
        examples=[utils.enums.codigos.lead_cod_enum.PrincipalCod.NAO],
    )
    lead: Optional[utils.enums.codigos.lead_cod_enum.LeadCod] = Field(
        default=utils.enums.codigos.lead_cod_enum.LeadCod.SIM,
        description="ID do tipo de contato.",
        examples=[utils.enums.codigos.lead_cod_enum.LeadCod.SIM],
    )
    tipo_pessoa: Optional[str] = Field(
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
    id_filial: Optional[PositiveInt] = Field(
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
    cep: str = Field(
        max_length=20,
        description="CEP do potencial cliente associado ao lead.",
        examples=["12345-678"],
    )
    endereco: str = Field(
        max_length=200,
        description="Endereço do potencial cliente associado ao lead.",
        examples=["Rua do Lead"],
    )
    numero: Optional[Union[str, PositiveInt]] = Field(
        default="S/N",
        description="Número da casa do potencial cliente associado ao lead.",
        examples=["123"],
    )
    bairro: str = Field(
        max_length=200,
        description="Bairro do potencial cliente associado ao lead.",
        examples=["Bairro do Lead"],
    )
    uf: Optional[PositiveInt] = Field(
        default=10, description="UF do potencial cliente."
    )
    cnpj_cpf: str = Field(
        max_length=30,
        description="CNPJ ou CPF do potencial cliente associado ao lead.",
        examples=["123.456.789-00"],
    )
    cidade: Optional[PositiveInt] = Field(
        utils.Default.ID_CIDADE_JACOBINA,
        description="ID da cidade associada ao lead.",
        examples=[utils.Default.ID_CIDADE_JACOBINA],
    )
    id_vd_contrato: Optional[PositiveInt] = Field(
        utils.Default.ID_VD_CONTRATO,
        description="ID do plano de contrato associado ao lead.",
        examples=[utils.Default.ID_VD_CONTRATO],
    )
    id_responsavel: Optional[PositiveInt] = Field(
        utils.Default.ID_RESPONSAVEL_ARCEUS,
        description="ID do responsável técnico associado ao lead.",
        examples=[utils.Default.ID_RESPONSAVEL_ARCEUS],
    )
    email: EmailStr = Field(
        description="Email do potencial cliente associado ao lead.",
        examples=["exemplo@examplo.com"],
    )
    id_candidato_tipo: Optional[PositiveInt] = Field(
        default=utils.Default.ID_CANAL_VENDA,
        description="Canal de venda",
        examples=[utils.Default.ID_CANAL_VENDA],
    )

    @field_serializer("ativo")
    def formatar_ativo(self, v):
        return str.upper(v)

    @field_serializer("principal")
    def formatar_principal(self, v):
        return str.upper(v)

    @field_serializer("tipo_pessoa")
    def formatar_tipo_pessoa(self, v):
        return str.upper(v)


class LeadCreate(BaseModel):
    id: PositiveInt = Field(description="ID do lead criado.", examples=[12345])
