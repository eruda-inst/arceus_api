from typing import Annotated
from .. import services, schemas
from fastapi import APIRouter, Query, status, Body

comercial_router = APIRouter(prefix="/comercial", tags=["Comercial"])


@comercial_router.get(
    path="/status_acesso", summary="Obtém status de acesso do contrato."
)
async def get_status_acesso(
    id_contrato: Annotated[int, Query(ge=1, description="ID do contrato.")],
) -> schemas.StatusAcessoOut:
    """
    Obtém status de acesso de um contrato, atravé do ID do contrato."
    """
    return await services.ComercialService.get_status_acesso(id_contrato=id_contrato)


@comercial_router.get(
    path="/contratos",
    summary="Obtém contratos de um cliente, por meio de protocolo de atendimento ou CPF/CNPJ.",
)
async def get_contratos(
    protocolo: Annotated[
        str | None,
        Query(min_length=12, max_length=12, description="Protocolo de atendimento."),
    ] = None,
    cnpj_cpf: Annotated[
        str | None, Query(description="CPF ou CNPJ do cliente.")
    ] = None,
    page: Annotated[int | None, Query(ge=1, description="Número da página.")] = 1,
    per_page: Annotated[int | None, Query(ge=1, description="Itens por página.")] = 10,
) -> schemas.ComercialContratoListOut:
    """
    Obtém contratos de todos os clientes, atravé de protocolo de atendimento ou CPF/CNPJ.
    """
    return await services.ComercialService.get_contratos(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        page=page,
        per_page=per_page,
    )


@comercial_router.post(
    path="/leads", status_code=status.HTTP_201_CREATED, summary="Cadastra novo lead."
)
async def post_leads(
    lead: Annotated[schemas.LeadIn, Body(description="Lead a ser cadastrado.")],
) -> schemas.LeadCreate:
    """
    Cadastra novo lead e retorna o ID do lead criado.
    """
    return await services.ComercialService.post_leads(lead=lead)


@comercial_router.get(
    path="/cliente_existe", summary="Verifica se um cliente existe no Opa."
)
async def cliente_existe(
    cpf_cnpj: Annotated[str, Query(description="CPF ou CNPJ.")],
) -> schemas.ClienteExisteOut:
    """
    Verifica se um cliente existe no Opa, através do CPF/CNPJ.
    """
    return await services.ComercialService.cliente_existe(cpf_cnpj=cpf_cnpj)


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@comercial_router.put(
    path="/leads", summary="Atualiza um ou mais campos associado a um lead específico."
)
async def put_lead(
    cnpj_cpf: Annotated[str, Query(description="CPF ou CNPJ associado ao lead.")],
    lead: Annotated[schemas.LeadUpdate, Body(description="Dados do lead.")],
) -> schemas.LeadOut:
    """
    Atualiza um ou mais campos associado a um lead específico, baseado no CPF/CNPJ.
    """
    return await services.ComercialService.put_lead(cnpj_cpf=cnpj_cpf, lead=lead)
