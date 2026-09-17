"""
Router for village (Vila) endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query
from pydantic import NonNegativeInt

from .. import deps, schemas, services

village_router = APIRouter(prefix="/vila", tags=["Vila"])


# Query parameter aliases
NumeroResidencia = Annotated[int, Query(ge=1, description="Número da residência")]
Pppoe = Annotated[str, Query(description="PPPOE associado ao cliente")]
# IDs NonNegativeInt, because IXC
IdLogin = Annotated[NonNegativeInt, Query(description="ID login associado ao cliente")]
GetCredsDeps = Annotated[bool, Depends(deps.get_creds)]


@village_router.get(
    path="/contrato/numero-residencia/{numero_residencia}",
    summary="Obtém contrato de um cliente",
)
async def get_contract_by_residence_number(
    _: GetCredsDeps,
    numero_residencia: Annotated[int, Path(ge=1, description="Número da residência")],
) -> schemas.VillageContractOutSchema:
    """
    Obtém contrato de um cliente, através do número da residência
    """
    return await services.VillageService.get_contract(
        residence_number=numero_residencia
    )


@village_router.get(
    path="/contrato/pppoe/{pppoe}", summary="Obtém contrato de um cliente"
)
async def get_contract_by_pppoe(
    _: GetCredsDeps,
    pppoe: Annotated[str, Path(description="PPPOE do login")],
) -> schemas.VillageContractOutSchema:
    """
    Obtém contrato de um cliente, através do PPPOE
    """
    return await services.VillageService.get_contract(pppoe=pppoe)


@village_router.get(path="/servidor-dns", summary="Obtém servidor DNS de um cliente")
async def get_dns_server(_: GetCredsDeps, id_login: IdLogin) -> schemas.DnsServerOut:
    """
    Obtém servidor DNS de um cliente, a partir do ID de login
    """
    return await services.SupportService.get_dns_server(login_id=id_login)


@village_router.get(path="/tem-ipv6", summary="Verifica se o cliente possui IPV6")
async def get_has_ipv6(_: GetCredsDeps, id_login: IdLogin) -> schemas.HasIPV6OutSchema:
    """
    Verifica se o cliente possui IPV6 ativo, a partir do ID de login
    """
    return await services.SupportService.get_has_ipv6(login_id=id_login)


@village_router.get(path="/uptime", summary="Obtém uptime de um dispositivo")
async def get_uptime(_: GetCredsDeps, id_login: IdLogin) -> schemas.UptimeOutSchema:
    """
    Obtém uptime de um cliente, a partir do ID de login
    """
    return await services.SupportService.get_uptime(login_id=id_login)


@village_router.get(path="/sinal-fibra", summary="Obtém RX e TX do sinal da fibra")
async def get_fiber_signal(
    _: GetCredsDeps, id_login: IdLogin
) -> schemas.FiberSignalOutSchema:
    """
    Obtém taxas de transmissão e de recepção do sinal da fibra, a partir do ID de login
    """
    return await services.SupportService.get_fiber_signal(login_id=id_login)


@village_router.get(
    path="/status-conexao", summary="Obtém status da conexão de um cliente"
)
async def get_connection_status(
    _: GetCredsDeps, id_login: IdLogin
) -> schemas.ConnectionStatusOutSchema:
    """
    Obtém status da conexão de um cliente, através do ID de login
    """
    return await services.SupportService.get_connection_status(login_id=id_login)


@village_router.get(path="/status-onu", summary="Obtém status da ONU de um cliente")
async def get_onu_status(
    _: GetCredsDeps, id_login: IdLogin
) -> schemas.OnuStatusOutSchema:
    """
    Obtém status da ONU de um cliente, através do ID de login
    """
    return await services.SupportService.get_onu_status(login_id=id_login)


@village_router.get(
    path="/atendimentos", summary="Obtém atendimentos abertos de um cliente"
)
async def get_tickets(
    _: GetCredsDeps,
    id_login: IdLogin,
    pagina: Annotated[int, Query(ge=1, description="Número da página")] = 1,
    itens_por_pagina: Annotated[int, Query(ge=1, description="Itens por página")] = 10,
) -> schemas.ListOutSchema[schemas.TicketOutSchema]:
    """
    Obtém atendimentos abertos de um cliente, através do ID de login
    """
    return await services.SupportService.get_tickets(
        login_id=id_login,
        page=pagina,
        items_per_page=itens_por_pagina,
    )


@village_router.post(path="/limpar-mac", summary="Limpa MAC Address de um cliente")
async def post_clear_mac(
    _: GetCredsDeps, id_login: IdLogin
) -> schemas.MessageOutSchema:
    """
    Limpa MAC Address de um cliente, através do ID de login
    """
    return await services.SupportService.post_clear_mac(login_id=id_login)


@village_router.post(path="/desconectar-cliente", summary="Desconecta um cliente")
async def post_disconnect_customer(
    _: GetCredsDeps, id_login: IdLogin
) -> schemas.MessageOutSchema:
    """
    Desconecta um cliente, através do ID de login
    """
    return await services.SupportService.post_disconnect_customer(login_id=id_login)


@village_router.post(
    path="/atendimentos", summary="Obtém atendimentos abertos de um cliente"
)
async def post_tickets(
    _: GetCredsDeps,
    atendimento: Annotated[
        schemas.TicketInSchema, Body(description="Dados do atendimento")
    ],
) -> schemas.TicketOutSchema:
    """
    Abre ticket de atendimento, através de dados do atendimento
    """
    return await services.SupportService.post_tickets(ticket=atendimento)


@village_router.patch(path="/dados-wifi", summary="Atualiza dados wifi de um cliente")
async def patch_wifi_data(
    _: GetCredsDeps,
    id_login: IdLogin,
    ssid: Annotated[str | None, Body(description="Novo SSID da rede wifi")] = None,
    senha_ssid: Annotated[
        str | None, Body(description="Nova senha da rede wifi")
    ] = None,
) -> schemas.MessageOutSchema:
    """
    Atualiza dados da rede wifi 2.5G e 5G de um cliente
    """
    return await services.SupportService.patch_wifi_data(
        login_id=id_login, ssid=ssid, ssid_pass=senha_ssid
    )
