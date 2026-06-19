from typing import Annotated
from .. import schemas, services
from fastapi import APIRouter, Query, status, Path, Body

suporte_router = APIRouter(prefix="/suporte", tags=["Suporte"])


@suporte_router.get(path="/contratos", summary="Obtém contratos ativos de um cliente.")
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
) -> schemas.SuporteContratoListOut:
    """
    Obtém contratos ativos de todos os clientes, atravé de protocolo de atendimento.
    """
    return await services.SuporteService.get_contratos(
        protocolo=protocolo, cnpj_cpf=cnpj_cpf, page=page, per_page=per_page
    )


@suporte_router.get(
    path="/status_conexao", summary="Obtém status de conexão de um cliente."
)
async def get_status_conexao(
    id_login: Annotated[
        int, Query(ge=1, description="ID de login do cliente no IXCSoft.")
    ],
) -> schemas.StatusConexaoOut:
    """
    Obtém status de conexão de um cliente, atravé do ID de login.
    """
    return await services.SuporteService.get_status_conexao(id_login=id_login)


@suporte_router.get(
    path="/status_onu", summary="Obtém status de ONU (sinal rx) de um cliente."
)
async def get_status_onu(
    id_login: Annotated[
        int | None,
        Query(ge=1, description="ID de login do cliente no IXCSoft."),
    ] = None,
    mac_onu: Annotated[
        str | None,
        Query(min_length=12, max_length=12, description="MAC Address da ONU."),
    ] = None,
) -> schemas.StatusONUOut:
    """
    Obtém status de ONU (sinal rx) de um cliente, atravé do ID de login, ou MAC Address de ONU.
    """
    return await services.SuporteService.get_status_onu(
        id_login=id_login, mac_onu=mac_onu
    )


@suporte_router.post(
    path="/desconectar_cliente", summary="Envia sinal de desconexão para um cliente."
)
async def post_desconectar_cliente(
    id_login: Annotated[
        int, Query(ge=1, description="ID de login do cliente no IXCSoft.")
    ],
) -> schemas.MensagemOut:
    """
    Envia sinal de desconexão para um cliente, atravé do ID de login.
    """
    return await services.SuporteService.post_desconectar_cliente(id_login=id_login)


@suporte_router.get(
    path="/atendimentos", summary="Checa atendimentos abertos de um cliente."
)
async def get_atendimentos(
    id_login: Annotated[
        int, Query(ge=1, description="ID de login do cliente no IXCSoft.")
    ],
    page: Annotated[int | None, Query(ge=1, description="Número da página.")] = 1,
    per_page: Annotated[int | None, Query(ge=1, description="Itens por página.")] = 10,
) -> schemas.AtendimentoOut:
    """
    Checa atendimentos abertos de um cliente, atravé do ID de login.
    """
    return await services.SuporteService.get_atendimentos(
        id_login=id_login, page=page, per_page=per_page
    )


@suporte_router.post(
    path="/atendimentos",
    status_code=status.HTTP_201_CREATED,
    summary="Abre ticket de atendimento.",
)
async def post_atendimentos(
    atendimento: Annotated[
        schemas.AtendimentoIn, Body(description="Dados do atendimento.")
    ],
) -> schemas.AtendimentoCreate:
    """
    Abre ticket de atendimento, atravé de dados do atendimento.
    """
    return await services.SuporteService.post_atendimentos(atendimento=atendimento)


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@suporte_router.put(
    path="/ip/{id_login}",
    summary="Atualiza um ou mais campos associado a um login específico.",
)
async def put_ip(
    id_login: Annotated[int, Path(ge=1, description="ID de login.")],
    ip: Annotated[str | None, Body(description="IP do login a ser atualizado.")] = "",
    pool_radius: Annotated[
        str | None, Body(description="Radius do login a ser atualizado.")
    ] = "",
) -> schemas.MensagemOut:
    """
    Atualiza um ou mais campos associado a um login específico, por meio do ID de login.
    """
    return await services.SuporteService.put_ip(
        id_login=id_login, ip=ip, pool_radius=pool_radius
    )


@suporte_router.post(path="/limpar_mac", summary="Limpa MAC Address.")
async def post_limpar_mac(
    id_login: Annotated[
        int, Query(ge=1, description="ID de login do cliente no IXCSoft.")
    ],
) -> schemas.MensagemOut:
    """
    Limpa MAC Address, atravé do ID de login.
    """
    return await services.SuporteService.post_limpar_mac(id_login=id_login)


@suporte_router.get(path="/dados_wifi", summary="Obtém dados de WiFi de um cliente.")
async def get_dados_wifi(
    id_login: Annotated[
        int, Query(ge=1, description="ID de login do cliente no IXCSoft.")
    ],
) -> schemas.WifiOut:
    """
    Obtém dados de WiFi de um cliente, atravé do ID de login.
    """
    return await services.SuporteService.get_dados_wifi(id_login=id_login)
