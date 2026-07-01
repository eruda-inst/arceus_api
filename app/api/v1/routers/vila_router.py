from typing import Annotated
from .. import services, schemas
from fastapi import APIRouter, Query

vila_router = APIRouter(prefix="/vila", tags=["Vila"])

NumeroResidencia = Annotated[int, Query(ge=1, description="Número da residência.")]
Pagina = Annotated[int, Query(ge=1, description="Número da página.")]
ItensPorPagina = Annotated[int, Query(ge=1, description="Itens por página.")]


@vila_router.get(
    path="/status_conexao", summary="Obtém status da conexão de um cliente."
)
async def get_status_conexao(
    numero_residencia: NumeroResidencia,
) -> schemas.NewStatusConexaoOut:
    """
    Obtém status da conexão de um cliente, através do número da residência.
    """
    return await services.VilaService.get_status_conexao(
        numero_residencia=numero_residencia
    )


@vila_router.get(path="/status_onu", summary="Obtém status da ONU de um cliente.")
async def get_status_onu(numero_residencia: NumeroResidencia) -> schemas.StatusOnuOut:
    """
    Obtém status da ONU de um cliente, através do número da residência.
    """
    return await services.VilaService.get_status_onu(
        numero_residencia=numero_residencia
    )


@vila_router.get(path="/dados_wifi", summary="Obtém dados do WiFi de um cliente.")
async def get_dados_wifi(numero_residencia: NumeroResidencia) -> schemas.NewWifiOut:
    """
    Obtém dados do WiFi de um cliente, através do número da residência.
    """
    return await services.VilaService.get_dados_wifi(
        numero_residencia=numero_residencia
    )


@vila_router.get(
    path="/atendimentos", summary="Obtém atendimentos abertos de um cliente."
)
async def get_atendimentos(
    numero_residencia: NumeroResidencia,
    pagina: Pagina | None = 1,
    itens_por_pagina: ItensPorPagina | None = 10,
) -> schemas.AtendimentoOut:
    """
    Obtém atendimentos abertos de um cliente, através do número da residência.
    """
    return await services.VilaService.get_atendimentos(
        numero_residencia=numero_residencia, page=pagina, per_page=itens_por_pagina
    )


@vila_router.post(path="/limpar_mac", summary="Limpa MAC Address de um cliente.")
async def post_limpar_mac(numero_residencia: NumeroResidencia) -> schemas.MensagemOut:
    """
    Limpa MAC Address de um cliente, através do número da residência.
    """
    return await services.VilaService.post_limpar_mac(
        numero_residencia=numero_residencia
    )


@vila_router.post(path="/desconectar_cliente", summary="Desconecta um cliente.")
async def post_desconectar_cliente(
    numero_residencia: NumeroResidencia,
) -> schemas.MensagemOut:
    """
    Desconecta um cliente, através do número da residência.
    """
    return await services.VilaService.post_desconectar_cliente(
        numero_residencia=numero_residencia
    )
