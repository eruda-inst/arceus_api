from typing import Annotated

from fastapi import APIRouter, Body, Path, Query, status

from .. import schemas, services, utils

suporte_router = APIRouter(prefix="/suporte", tags=["Suporte"])

# IDs NonNegativeInt, pois o IXC é quebrado
IdLogin = Annotated[int, Query(ge=0, description="ID de login do cliente")]


@suporte_router.get(path="/contratos", summary="Obtém contratos de um cliente")
async def get_contratos(
    protocolo: utils.Protocolo | None = None,
    cnpj_cpf: utils.CnpjCpf | None = None,
    pagina: utils.Pagina | None = 1,
    itens_por_pagina: utils.ItensPorPagina | None = 10,
) -> schemas.ListOut[schemas.ContratoOut]:
    """
    Obtém contratos de um cliente, através de protocolo de atendimento ou CPF/CNPJ
    """
    return await services.SuporteService.get_contratos(
        protocolo=protocolo,
        cnpj_cpf=cnpj_cpf,
        pagina=pagina,
        itens_por_pagina=itens_por_pagina,
    )


@suporte_router.get(
    path="/status_conexao", summary="Obtém status de conexão de um cliente"
)
async def get_status_conexao(id_login: IdLogin) -> schemas.StatusConexaoOut:
    """
    Obtém status de conexão de um cliente, através do id de login
    """
    return await services.SuporteService.get_status_conexao(id_login=id_login)


@suporte_router.get(path="/status_onu", summary="Obtém status de ONU de um cliente")
async def get_status_onu(
    id_login: IdLogin | None = None,
    mac_onu: Annotated[
        str | None,
        Query(min_length=12, max_length=12, description="MAC Address da ONU."),
    ] = None,
) -> schemas.StatusOnuOut:
    """
    Obtém status de ONU de um cliente, através do ID de login ou MAC Address
    """
    return await services.SuporteService.get_status_onu(
        id_login=id_login, mac_onu=mac_onu
    )


@suporte_router.get(path="/dados_wifi", summary="Obtém dados do WiFi de um cliente")
async def get_dados_wifi(id_login: IdLogin) -> schemas.WifiOut:
    """
    Obtém dados do WiFi de um cliente, através do ID de login
    """
    return await services.SuporteService.get_dados_wifi(id_login=id_login)


@suporte_router.get(
    path="/atendimentos", summary="Obtém atendimentos abertos de um cliente"
)
async def get_atendimentos(
    id_login: IdLogin,
    pagina: utils.Pagina | None = 1,
    itens_por_pagina: utils.ItensPorPagina | None = 10,
) -> schemas.ListOut[schemas.AtendimentoOut]:
    """
    Obtém atendimentos abertos de um cliente, através do ID de login
    """
    return await services.SuporteService.get_atendimentos(
        id_login=id_login, pagina=pagina, itens_por_pagina=itens_por_pagina
    )


@suporte_router.post(
    path="/atendimentos",
    status_code=status.HTTP_201_CREATED,
    summary="Abre um atendimento para um cliente",
)
async def post_atendimentos(
    atendimento: Annotated[
        schemas.AtendimentoIn, Body(description="Dados do atendimento")
    ],
) -> schemas.AtendimentoOut:
    """
    Abre um atendimento para um cliente, atravé de dados do atendimento
    """
    return await services.SuporteService.post_atendimentos(atendimento=atendimento)


@suporte_router.post(
    path="/desconectar_cliente", summary="Envia sinal de desconexão para um cliente"
)
async def post_desconectar_cliente(id_login: IdLogin) -> schemas.MensagemOut:
    """
    Envia sinal de desconexão para um cliente, através do id de login
    """
    return await services.SuporteService.post_desconectar_cliente(id_login=id_login)


@suporte_router.post(path="/limpar_mac", summary="Limpa MAC Address")
async def post_limpar_mac(id_login: IdLogin) -> schemas.MensagemOut:
    """
    Limpa MAC Address, através do id de login
    """
    return await services.SuporteService.post_limpar_mac(id_login=id_login)


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@suporte_router.put(path="/ip/{id_login}", summary="Atualiza IP e Radius de um login")
async def put_ip(
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_login: Annotated[int, Path(ge=0, description="ID de login")],
    ip: Annotated[str | None, Body(description="IP do login a ser atualizado")] = None,
    pool_radius: Annotated[
        str | None, Body(description="Radius do login a ser atualizado")
    ] = None,
) -> schemas.IpOut:
    """
    Atualiza IP e Radius de um login, através do id de login
    """
    return await services.SuporteService.put_ip(
        id_login=id_login, ip=ip, pool_radius=pool_radius
    )
