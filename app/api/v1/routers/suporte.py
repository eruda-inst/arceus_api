from .. import schemas
from typing import Optional
from ..utils import SortOrder
from pydantic import PositiveInt
from ..services import SuporteService
from fastapi import APIRouter, Query, status, Path, Body


suporte_router = APIRouter()
suporte_service = SuporteService()


@suporte_router.get(
    path="/contratos",
    response_model=schemas.SuporteContratoListOut,
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
) -> schemas.SuporteContratoListOut:
    return await suporte_service.get_contratos_ativos(
        protocolo=protocolo,
        page=page,
        per_page=per_page,
        sortname=sortname,
        sortorder=sortorder,
    )


@suporte_router.get(
    path="/status_conexao",
    response_model=schemas.StatusConexaoOut,
    summary="Obtém status de conexão de um cliente, através de ID de login.",
)
async def get_status_conexao(
    id_login: PositiveInt = Query(
        ge=1, description="ID de login do cliente no IXCSoft."
    ),
) -> schemas.StatusConexaoOut:
    return await suporte_service.get_status_conexao(id_login=id_login)


@suporte_router.get(
    path="/status_onu",
    response_model=schemas.StatusONUOut,
    summary="Obtém status de ONU (sinal rx) de um cliente, através de ID de login, ou MAC Address de ONU.",
)
async def get_status_onu(
    id_login: Optional[PositiveInt] = Query(
        ge=1, default=None, description="ID de login do cliente no IXCSoft."
    ),
    mac_onu: Optional[str] = Query(
        min_length=12, max_length=12, default=None, description="MAC Address da ONU."
    ),
) -> schemas.StatusONUOut:
    return await suporte_service.get_status_onu(id_login=id_login, mac_onu=mac_onu)


@suporte_router.post(
    path="/desconectar_cliente",
    response_model=schemas.MensagemOut,
    summary="Envia sinal de desconexão para um cliente, através de ID de login.",
)
async def post_desconectar_cliente(
    id_login: PositiveInt = Query(
        ge=1, description="ID de login do cliente no IXCSoft."
    ),
) -> schemas.MensagemOut:
    return await suporte_service.post_desconectar_cliente(id_login=id_login)


@suporte_router.get(
    path="/atendimentos",
    response_model=schemas.AtendimentoOut,
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
) -> schemas.AtendimentoOut:
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
    response_model=schemas.AtendimentoCreate,
    summary="Abre ticket de atendimento, através de dados do atendimento.",
)
async def post_atendimentos(
    atendimento: schemas.AtendimentoIn,
) -> schemas.AtendimentoCreate:
    return await suporte_service.post_atendimentos(atendimento=atendimento)


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@suporte_router.put(
    path="/logins/{id}",
    response_model=schemas.MensagemOut,
    summary="Atualiza um ou mais campos associado a um login específico, por meio do ID de login.",
)
async def patch_logins(
    id: PositiveInt = Path(ge=1, description="ID de login."),
    login: schemas.LoginUpdate = Body(
        ge=1, description="Campos de login a serem atualizados."
    ),
) -> schemas.MensagemOut:
    return await suporte_service.patch_logins(id=id, login=login)


@suporte_router.post(
    path="/limpar_mac",
    response_model=schemas.MensagemOut,
    summary="Limpa MAC Address, através do ID de login.",
)
async def limpar_mac(
    id_login: PositiveInt = Query(
        ge=1, description="ID de login do cliente no IXCSoft."
    )
) -> schemas.MensagemOut:
    return await suporte_service.post_limpar_mac(id_login=id_login)
