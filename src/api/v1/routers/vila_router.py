from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query
from pydantic import NonNegativeInt

from .. import deps, schemas, services

vila_router = APIRouter(prefix="/vila", tags=["Vila"])


NumeroResidencia = Annotated[int, Query(ge=1, description="Número da residência")]
Pppoe = Annotated[str, Query(description="PPPOE associado ao cliente")]
# IDs NonNegativeInt, because IXC
IdLogin = Annotated[NonNegativeInt, Query(description="ID login associado ao cliente")]
GetCredsDeps = Annotated[bool, Depends(deps.get_creds)]


@vila_router.get(
    path="/contrato/numero-residencia/{numero_residencia}",
    summary="Obtém contrato de um cliente",
)
async def get_contrato_by_numero_residencia(
    _: GetCredsDeps,
    numero_residencia: Annotated[int, Path(ge=1, description="Número da residência")],
) -> schemas.VilaContratoOutSchema:
    """
    Obtém contrato de um cliente, através do número da residência
    """
    return await services.VilaService.get_contrato(numero_residencia=numero_residencia)


@vila_router.get(path="/contrato/pppoe/{pppoe}", summary="Obtém contrato de um cliente")
async def get_contrato_by_ppoe(
    _: GetCredsDeps,
    pppoe: Annotated[str, Path(description="PPPOE do login")],
) -> schemas.VilaContratoOutSchema:
    """
    Obtém contrato de um cliente, através do PPPOE
    """
    return await services.VilaService.get_contrato(pppoe=pppoe)


@vila_router.get(path="/servidor-dns", summary="Obtém servidor DNS de um cliente")
async def get_dns_server(_: GetCredsDeps, id_login: IdLogin) -> schemas.DnsServerOut:
    """
    Obtém servidor DNS de um cliente, a partir do ID de login
    """
    return await services.SuporteService.get_dns_server(id_login=id_login)


@vila_router.get(path="/tem-ipv6", summary="Verifica se o cliente possui IPV6")
async def get_has_ipv6(_: GetCredsDeps, id_login: IdLogin) -> schemas.TemIPV6OutSchema:
    """
    Verifica se o cliente possui IPV6 ativo, a partir do ID de login
    """
    return await services.SuporteService.get_has_ipv6(id_login=id_login)


@vila_router.get(path="/uptime", summary="Obtém uptime de um dispositivo")
async def get_uptime(_: GetCredsDeps, id_login: IdLogin) -> schemas.UptimeOutSchema:
    """
    Obtém uptime de um cliente, a partir do ID de login
    """
    return await services.SuporteService.get_uptime(id_login=id_login)


@vila_router.get(
    path="/status-conexao", summary="Obtém status da conexão de um cliente"
)
async def get_status_conexao(
    _: GetCredsDeps, id_login: IdLogin
) -> schemas.StatusConexaoOutSchema:
    """
    Obtém status da conexão de um cliente, através do ID de login
    """
    return await services.VilaService.get_status_conexao(id_login=id_login)


@vila_router.get(path="/status-onu", summary="Obtém status da ONU de um cliente")
async def get_status_onu(
    _: GetCredsDeps, id_login: IdLogin
) -> schemas.StatusOnuOutSchema:
    """
    Obtém status da ONU de um cliente, através do ID de login
    """
    return await services.VilaService.get_status_onu(id_login=id_login)


@vila_router.get(
    path="/atendimentos", summary="Obtém atendimentos abertos de um cliente"
)
async def get_atendimentos(
    _: GetCredsDeps,
    id_login: IdLogin,
    pagina: Annotated[int, Query(ge=1, description="Número da página")] = 1,
    itens_por_pagina: Annotated[int, Query(ge=1, description="Itens por página")] = 10,
) -> schemas.ListOutSchema[schemas.AtendimentoOutSchema]:
    """
    Obtém atendimentos abertos de um cliente, através do ID de login
    """
    return await services.VilaService.get_atendimentos(
        id_login=id_login,
        pagina=pagina,
        itens_por_pagina=itens_por_pagina,
    )


@vila_router.post(path="/limpar-mac", summary="Limpa MAC Address de um cliente")
async def post_limpar_mac(
    _: GetCredsDeps, id_login: IdLogin
) -> schemas.MensagemOutSchema:
    """
    Limpa MAC Address de um cliente, através do ID de login
    """
    return await services.VilaService.post_limpar_mac(id_login=id_login)


@vila_router.post(path="/desconectar-cliente", summary="Desconecta um cliente")
async def post_desconectar_cliente(
    _: GetCredsDeps, id_login: IdLogin
) -> schemas.MensagemOutSchema:
    """
    Desconecta um cliente, através do ID de login
    """
    return await services.VilaService.post_desconectar_cliente(id_login=id_login)


@vila_router.post(
    path="/atendimentos", summary="Obtém atendimentos abertos de um cliente"
)
async def post_atendimentos(
    _: GetCredsDeps,
    atendimento: Annotated[
        schemas.AtendimentoInSchema, Body(description="Dados do atendimento")
    ],
) -> schemas.AtendimentoOutSchema:
    """
    Abre ticket de atendimento, através de dados do atendimento
    """
    return await services.VilaService.post_atendimentos(atendimento=atendimento)


@vila_router.patch(path="/dados-wifi", summary="Atualiza dados wifi de um cliente")
async def patch_dados_wifi(
    _: GetCredsDeps,
    id_login: IdLogin,
    ssid: Annotated[str | None, Body(description="Novo SSID da rede wifi")] = None,
    senha_ssid: Annotated[
        str | None, Body(description="Nova senha da rede wifi")
    ] = None,
) -> schemas.MensagemOutSchema:
    """
    Atualiza dados da rede wifi 2.5G e 5G de um cliente
    """
    return await services.SuporteService.patch_dados_wifi(
        id_login=id_login, ssid=ssid, senha_ssid=senha_ssid
    )
