"""
Router for support endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Body, Path, Query, status

from .. import schemas, services, utils

support_router = APIRouter(prefix="/suporte", tags=["Suporte"])

# IDs NonNegativeInt, because IXC
IdLogin = Annotated[int, Query(ge=0, description="ID de login do cliente")]


@support_router.get(
    path="/atendimentos", summary="Obtém atendimentos abertos de um cliente"
)
async def get_tickets(
    id_login: IdLogin,
    pagina: utils.Page = 1,
    itens_por_pagina: utils.ItemsPerPage = 10,
) -> schemas.ListOutSchema[schemas.TicketOutSchema]:
    """Obtém atendimentos abertos de um cliente, através do ID de login"""
    return await services.SupportService.get_tickets(
        login_id=id_login, page=pagina, items_per_page=itens_por_pagina
    )


@support_router.post(
    path="/atendimentos",
    status_code=status.HTTP_201_CREATED,
    summary="Abre um atendimento para um cliente",
)
async def post_tickets(
    atendimento: Annotated[
        schemas.TicketInSchema, Body(description="Dados do atendimento")
    ],
) -> schemas.TicketOutSchema:
    """Abre um atendimento para um cliente, atravé de dados do atendimento"""
    return await services.SupportService.post_tickets(ticket=atendimento)


@support_router.get(path="/contratos", summary="Obtém contratos de um cliente")
async def get_contracts(
    protocolo: utils.Protocol | None = None,
    cnpj_cpf: utils.CnpjCpf | None = None,
    pagina: utils.Page = 1,
    itens_por_pagina: utils.ItemsPerPage = 10,
) -> schemas.ListOutSchema[schemas.ContractOutSchema]:
    """Obtém contratos de um cliente, através de protocolo de atendimento ou CPF/CNPJ"""
    return await services.SupportService.get_contracts(
        protocol=protocolo,
        cnpj_cpf=cnpj_cpf,
        page=pagina,
        items_per_page=itens_por_pagina,
    )


@support_router.get(path="/dados-wifi", summary="Obtém dados do WiFi de um cliente")
async def get_wifi_data(id_login: IdLogin) -> schemas.WifiOutSchema:
    """Obtém dados do WiFi de um cliente, através do ID de login"""
    return await services.SupportService.get_wifi_data(login_id=id_login)


@support_router.patch(path="/dados-wifi", summary="Atualiza dados wifi de um cliente")
async def patch_wifi_data(
    id_login: IdLogin,
    ssid: Annotated[str | None, Body(description="Novo SSID da rede wifi")] = None,
    senha_ssid: Annotated[
        str | None, Body(description="Nova senha da rede wifi")
    ] = None,
) -> schemas.MessageOutSchema:
    """Atualiza dados da rede wifi 2G e 5G de um cliente"""
    return await services.SupportService.patch_wifi_data(
        login_id=id_login, ssid=ssid, ssid_pass=senha_ssid
    )


@support_router.post(
    path="/desconectar-cliente", summary="Envia sinal de desconexão para um cliente"
)
async def post_disconnect_customer(id_login: IdLogin) -> schemas.MessageOutSchema:
    """Envia sinal de desconexão para um cliente, através do id de login"""
    return await services.SupportService.post_disconnect_customer(login_id=id_login)


@support_router.patch(path="/ip/{id_login}", summary="Atualiza IP e Radius de um login")
async def patch_ip(
    # IDs NonNegativeInt, pois o IXC é quebrado
    id_login: Annotated[int, Path(ge=0, description="ID de login")],
    ip: Annotated[str | None, Body(description="IP do login a ser atualizado")] = None,
    pool_radius: Annotated[
        str | None, Body(description="Radius do login a ser atualizado")
    ] = None,
) -> schemas.IpOutSchema:
    """Atualiza IP e Radius de um login, através do id de login"""
    return await services.SupportService.patch_ip(
        login_id=id_login, ip=ip, pool_radius=pool_radius
    )


@support_router.post(path="/limpar-mac", summary="Limpa MAC Address")
async def post_clear_mac(id_login: IdLogin) -> schemas.MessageOutSchema:
    """Limpa MAC Address, através do id de login"""
    return await services.SupportService.post_clear_mac(login_id=id_login)


@support_router.get(path="/servidor-dns", summary="Obtém servidor DNS de um cliente")
async def get_dns_server(id_login: IdLogin) -> schemas.DnsServerOut:
    """Obtém servidor DNS de um cliente, através do ID de login"""
    return await services.SupportService.get_dns_server(login_id=id_login)


@support_router.get(path="/sinal-fibra", summary="Obtém RX e TX do sinal da fibra")
async def get_fiber_signal(id_login: IdLogin) -> schemas.FiberSignalOutSchema:
    """Obtém taxas de transmissão e de recepção do sinal da fibra, através do ID de login"""
    return await services.SupportService.get_fiber_signal(login_id=id_login)


@support_router.get(
    path="/status-conexao", summary="Obtém status de conexão de um cliente"
)
async def get_connection_status(id_login: IdLogin) -> schemas.ConnectionStatusOutSchema:
    """Obtém status de conexão de um cliente, através do ID de login"""
    return await services.SupportService.get_connection_status(login_id=id_login)


@support_router.get(path="/status-onu", summary="Obtém status de ONU de um cliente")
async def get_onu_status(
    id_login: IdLogin | None = None,
    mac_onu: Annotated[
        str | None,
        Query(description="MAC Address da ONU."),
    ] = None,
) -> schemas.OnuStatusOutSchema:
    """Obtém status de ONU de um cliente, através do ID de login ou MAC Address"""
    return await services.SupportService.get_onu_status(
        login_id=id_login, onu_mac=mac_onu
    )


@support_router.get(path="/tem-ipv6", summary="Verifica se o cliente possui IPV6")
async def get_has_ipv6(id_login: IdLogin) -> schemas.HasIPV6OutSchema:
    """Verifica se o cliente possui IPV6 ativo, através do ID de login"""
    return await services.SupportService.get_has_ipv6(login_id=id_login)


@support_router.get(path="/uptime", summary="Obtém uptime de um dispositivo")
async def get_uptime(id_login: IdLogin) -> schemas.UptimeOutSchema:
    """Obtém uptime de um cliente, através do ID de login"""
    return await services.SupportService.get_uptime(login_id=id_login)
