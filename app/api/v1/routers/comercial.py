from typing import Optional
from pydantic import PositiveInt
from .. import utils, services, schemas
from fastapi import APIRouter, Query, status, Body

comercial_router = APIRouter()
comercial_service = services.ComercialService()


@comercial_router.get(
    path="/status_acesso",
    response_model=schemas.StatusAcessoOut,
    summary="Obtém status de acesso, através de ID de contrato.",
)
async def get_status_acesso(
    id_contrato: PositiveInt = Query(ge=1, description="ID do contrato."),
) -> schemas.StatusAcessoOut:
    """
    Obtém o status de acesso de um contrato específico.

    Args:
        id_contrato: O ID do contrato a ser consultado.

    Returns:
        O status de acesso do contrato.
    """
    return await comercial_service.get_status_acesso(id_contrato=id_contrato)


@comercial_router.get(
    path="/contratos",
    response_model=schemas.ComercialContratoListOut,
    summary="Obtém contratos de um cliente, por meio de ID de login.",
)
async def get_contratos(
    protocolo: str = Query(
        min_length=12,
        max_length=12,
        description="Protocolo de atendimento do cliente no OpaSuite.",
    ),
    page: Optional[PositiveInt] = Query(
        ge=1, default=1, description="Número da página."
    ),
    per_page: Optional[PositiveInt] = Query(
        ge=1, default=10, description="Itens por página."
    ),
    sortname: Optional[str] = Query(
        default="cliente_contrato.id", description="Campo para ordenação."
    ),
    sortorder: Optional[utils.SortOrder] = Query(
        utils.SortOrder.ASC, description="Ordem da ordenação."
    ),
) -> schemas.ComercialContratoListOut:
    """
    Obtém a lista de contratos de um cliente, com base no protocolo de atendimento.

    Args:
        protocolo: O protocolo de atendimento do cliente no OpaSuite.
        page: O número da página para a paginação.
        per_page: A quantidade de itens por página.
        sortname: O campo pelo qual a lista será ordenada.
        sortorder: A ordem de ordenação (ascendente ou descendente).

    Returns:
        Uma lista paginada de contratos do cliente.
    """
    return await comercial_service.get_contratos(
        protocolo=protocolo,
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )


@comercial_router.post(
    path="/leads",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.LeadCreate,
    summary="Cadastra novo lead, a partir de lead submetido.",
)
async def post_leads(
    lead: schemas.LeadIn = Body(description="Lead a ser cadastrado."),
) -> schemas.LeadCreate:
    """
    Cadastra um novo lead no sistema.

    Args:
        lead: Os dados do lead a ser cadastrado.

    Returns:
        Os dados do lead recém-criado.
    """
    return await comercial_service.post_leads(lead=lead)
