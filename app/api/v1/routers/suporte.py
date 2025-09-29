from typing import Optional
from ..utils import SortOrder
from pydantic import PositiveInt
from ..services import SuporteService
from fastapi import APIRouter, Query, status, Path, Body
from ..schemas import (
    StatusConexaoOut,
    AtendimentoOut,
    AtendimentoIn,
    SuporteContratoListOut,
    StatusONUOut,
    AtendimentoCreate,
    LoginUpdate,
    MensagemOut,
)


suporte_router = APIRouter()
suporte_service = SuporteService()


@suporte_router.get(
    path="/contratos",
    response_model=SuporteContratoListOut,
    summary="Obtém contratos ativos de um cliente, através de protocolo de atendimento.",
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
    sortorder: Optional[SortOrder] = Query(
        default=SortOrder.ASC, description="Ordem da ordenação."
    ),
) -> SuporteContratoListOut:
    return await suporte_service.get_contratos_ativos(
        protocolo=protocolo,
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )


@suporte_router.get(
    path="/status_conexao",
    response_model=StatusConexaoOut,
    summary="Obtém status de conexão de um cliente, através de ID de login.",
)
async def get_status_conexao(
    id_login: PositiveInt = Query(
        ge=1, description="ID de login do cliente no IXCSoft."
    ),
) -> StatusConexaoOut:
    return await suporte_service.get_status_conexao(id_login=id_login)


@suporte_router.get(
    path="/status_onu",
    response_model=StatusONUOut,
    summary="Obtém status de ONU (sinal rx) de um cliente, através de ID de login, ou MAC Address de ONU.",
)
async def get_status_onu(
    id_login: Optional[PositiveInt] = Query(
        ge=1, default=None, description="ID de login do cliente no IXCSoft."
    ),
    mac_onu: Optional[str] = Query(
        min_length=12, max_length=12, default=None, description="MAC Address da ONU."
    ),
) -> StatusONUOut:
    return await suporte_service.get_status_onu(id_login=id_login, mac_onu=mac_onu)


@suporte_router.post(
    path="/desconectar_cliente",
    response_model=MensagemOut,
    summary="Envia sinal de desconexão para um cliente, através de ID de login.",
)
async def post_desconectar_cliente(
    id_login: PositiveInt = Query(
        ge=1, description="ID de login do cliente no IXCSoft."
    ),
) -> MensagemOut:
    return await suporte_service.post_desconectar_cliente(id_login=id_login)


@suporte_router.get(
    path="/atendimentos",
    response_model=AtendimentoOut,
    summary="Checa atendimentos abertos de um cliente, através de ID de login.",
)
async def get_atendimentos(
    id_login: PositiveInt = Query(
        ge=1, description="ID de login do cliente no IXCSoft."
    ),
    page: Optional[PositiveInt] = Query(
        ge=1, default=1, description="Número da página."
    ),
    per_page: Optional[PositiveInt] = Query(
        ge=1, default=10, description="Itens por página."
    ),
    sortname: Optional[str] = Query(
        default="su_ticket.id", description="Campo para ordenação."
    ),
    sortorder: Optional[SortOrder] = Query(
        default=SortOrder.ASC, description="Ordem da ordenação."
    ),
) -> AtendimentoOut:
    return await suporte_service.get_atendimentos_abertos(
        id_login=id_login,
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )


@suporte_router.post(
    path="/atendimentos",
    status_code=status.HTTP_201_CREATED,
    response_model=AtendimentoCreate,
    summary="Abre ticket de atendimento, através de dados do atendimento.",
)
async def post_atendimentos(atendimento: AtendimentoIn) -> AtendimentoCreate:
    return await suporte_service.post_atendimentos(atendimento=atendimento)


@suporte_router.patch(
    path="/logins/{id}",
    response_model=MensagemOut,
    summary="Atualiza um ou mais campos associado a um login específico, por meio do ID de login.",
)
async def patch_logins(
    id: PositiveInt = Path(ge=1, description="ID de login."),
    login: LoginUpdate = Body(ge=1, description="Campos de login a serem atualizados."),
) -> MensagemOut:
    return await suporte_service.patch_logins(id=id, login=login)
