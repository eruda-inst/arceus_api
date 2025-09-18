from typing import Optional
from ..utils import SortOrder
from ..services import SuporteService
from fastapi import APIRouter, Query, status
from ..schemas import (
    StatusConexaoOut,
    AtendimentoOut,
    AtendimentoIn,
    ContratoListOut,
    StatusONUOut,
    AtendimentoCreate
)


router  = APIRouter()
service = SuporteService()

@router.get("/contratos", summary="Obtém contratos ativos de um cliente, através de protocolo de atendimento.")
async def get_contratos(
    protocolo: str = Query(
        min_length=12,
        max_length=12,
        description="Protocolo de atendimento do cliente no OpaSuite.",
    ),
    page: Optional[int] = Query(
        ge=1,
        default=1,
        description="Número da página.",
    ),
    per_page: Optional[int] = Query(
        ge=1,
        default=10,
        description="Itens por página.",
    ),
    sortname: Optional[str] = Query(
        default="cliente_contrato.id",
        description="Campo para ordenação.",
    ),
    sortorder: Optional[SortOrder] = Query(
        default=SortOrder.ASC,
        description="Ordem da ordenação.",
    ),
) -> ContratoListOut:
    return await service.get_contratos_ativos(
        protocolo=protocolo,
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )

@router.get("/status_conexao", summary="Obtém status de conexão de um cliente, através de ID de login.")
async def get_status_conexao(
    id_login: int = Query(
        description="ID de login do cliente no IXCSoft.",
    ),
) -> StatusConexaoOut:
    return await service.get_status_conexao(
        id_login=id_login,
    )

@router.get("/status_onu", summary="Obtém status de ONU (sinal rx) de um cliente, através de ID de login, ou MAC Address de ONU.")
async def get_status_onu(
    id_login: Optional[int] = Query(
        default=None,
        description="ID de login do cliente no IXCSoft.",
    ),
    mac_onu: Optional[str] = Query(
        default=None,
        description="MAC Address da ONU.",
    ),
) -> StatusONUOut:
    return await service.get_status_onu(
        id_login=id_login,
        mac_onu=mac_onu,
    )

@router.post("/desconectar_cliente", status_code=status.HTTP_204_NO_CONTENT, summary="Envia sinal de desconexão para um cliente, através de ID de login.")
async def post_desconectar_cliente(
    id_login: int = Query(
        description="ID de login do cliente no IXCSoft.",
    ),
) -> None:
    return await service.post_desconectar_cliente(
        id_login=id_login,
    )

@router.get("/atendimentos", summary="Checa atendimentos abertos de um cliente, através de ID de login.")
async def get_atendimentos(
    id_login: int = Query(
        description="ID de login do cliente no IXCSoft.",
    ),
    page: Optional[int] = Query(
        ge=1,
        default=1,
        description="Número da página.",
    ),
    per_page: Optional[int] = Query(
        ge=1,
        default=10,
        description="Itens por página.",
    ),
    sortname: Optional[str] = Query(
        default="su_ticket.id",
        description="Campo para ordenação.",
    ),
    sortorder: Optional[SortOrder] = Query(
        default=SortOrder.ASC,
        description="Ordem da ordenação.",
    ),
) -> AtendimentoOut:
    return await service.get_atendimentos_abertos(
        id_login=id_login,
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )

@router.post("/atendimentos", status_code=status.HTTP_201_CREATED, summary="Abre ticket de atendimento, através de dados do atendimento.")
async def post_atendimentos(
    atendimento: AtendimentoIn,
) -> AtendimentoCreate:
    return await service.post_atendimentos(
        atendimento=atendimento,
    )