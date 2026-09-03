from typing import Annotated

from fastapi import APIRouter, Body, Path, Query
from pydantic import NonNegativeInt

from .. import schemas, services

vila_router = APIRouter(prefix="/vila", tags=["Vila"])

NumeroResidencia = Annotated[int, Query(ge=1, description="Número da residência")]
Pppoe = Annotated[str, Query(description="PPPOE associado ao cliente")]
# IDs NonNegativeInt, pois o IXC é quebrado
IdLogin = Annotated[NonNegativeInt, Query(description="ID login associado ao cliente")]


@vila_router.get(
    path="/contrato/numero-residencia/{numero_residencia}",
    summary="Obtém contrato de um cliente",
)
async def get_contrato_by_numero_residencia(
    numero_residencia: Annotated[int, Path(ge=1, description="Número da residência")],
) -> schemas.VilaContratoOutSchema:
    """
    Obtém contrato de um cliente, através do número da residência
    """
    return await services.VilaService.get_contrato(numero_residencia=numero_residencia)


@vila_router.get(path="/contrato/pppoe/{pppoe}", summary="Obtém contrato de um cliente")
async def get_contrato_by_ppoe(
    pppoe: Annotated[str, Path(description="PPPOE do login")],
) -> schemas.VilaContratoOutSchema:
    """
    Obtém contrato de um cliente, através do PPPOE
    """
    return await services.VilaService.get_contrato(pppoe=pppoe)


@vila_router.get(
    path="/status-conexao", summary="Obtém status da conexão de um cliente"
)
async def get_status_conexao(id_login: IdLogin) -> schemas.StatusConexaoOutSchema:
    """
    Obtém status da conexão de um cliente, através do ID de login
    """
    return await services.VilaService.get_status_conexao(id_login=id_login)


@vila_router.get(path="/status-onu", summary="Obtém status da ONU de um cliente")
async def get_status_onu(id_login: IdLogin) -> schemas.StatusOnuOutSchema:
    """
    Obtém status da ONU de um cliente, através do ID de login
    """
    return await services.VilaService.get_status_onu(id_login=id_login)


@vila_router.get(
    path="/atendimentos", summary="Obtém atendimentos abertos de um cliente"
)
async def get_atendimentos(
    id_login: IdLogin,
    pagina: Annotated[int | None, Query(ge=1, description="Número da página")] = 1,
    itens_por_pagina: Annotated[
        int | None, Query(ge=1, description="Itens por página")
    ] = 10,
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
async def post_limpar_mac(id_login: IdLogin) -> schemas.MensagemOutSchema:
    """
    Limpa MAC Address de um cliente, através do ID de login
    """
    return await services.VilaService.post_limpar_mac(id_login=id_login)


@vila_router.post(path="/desconectar-cliente", summary="Desconecta um cliente")
async def post_desconectar_cliente(id_login: IdLogin) -> schemas.MensagemOutSchema:
    """
    Desconecta um cliente, através do ID de login
    """
    return await services.VilaService.post_desconectar_cliente(id_login=id_login)


@vila_router.post(
    path="/atendimentos", summary="Obtém atendimentos abertos de um cliente"
)
async def post_atendimentos(
    atendimento: Annotated[
        schemas.AtendimentoInSchema, Body(description="Dados do atendimento")
    ],
) -> schemas.AtendimentoOutSchema:
    """
    Abre ticket de atendimento, através de dados do atendimento
    """
    return await services.VilaService.post_atendimentos(atendimento=atendimento)
