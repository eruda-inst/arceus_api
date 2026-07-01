from typing import Annotated
from .. import services, schemas
from fastapi import APIRouter, Query, Body

vila_router = APIRouter(prefix="/vila", tags=["Vila"])

NumeroResidencia = Annotated[int, Query(ge=1, description="Número da residência.")]
Pagina = Annotated[int, Query(ge=1, description="Número da página.")]
ItensPorPagina = Annotated[int, Query(ge=1, description="Itens por página.")]


@vila_router.get(
    path="/status_conexao", summary="Obtém status da conexão de um cliente."
)
async def get_status_conexao(
    numero_residencia: NumeroResidencia,
) -> schemas.StatusConexaoOut:
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
async def get_dados_wifi(numero_residencia: NumeroResidencia) -> schemas.WifiOut:
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


@vila_router.post(
    path="/atendimentos", summary="Obtém atendimentos abertos de um cliente."
)
async def post_atendimentos(
    atendimento: Annotated[
        schemas.AtendimentoIn, Body(description="Dados do atendimento.")
    ],
) -> schemas.AtendimentoCreate:
    """
    Abre ticket de atendimento, através de dados do atendimento.
    """
    return await services.VilaService.post_atendimentos(atendimento=atendimento)


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@vila_router.put(path="/ip", summary="Atualiza ip e pool radius de um login.")
async def put_ip(
    numero_residencia: NumeroResidencia,
    ip: Annotated[str | None, Body(description="IP do login a ser atualizado.")] = "",
    pool_radius: Annotated[
        str | None, Body(description="Pool radius do login a ser atualizado.")
    ] = "",
):
    """
    Atualiza ip e pool radius de um login, através do número da residência.
    """
    return await services.VilaService.put_ip(
        numero_residencia=numero_residencia, ip=ip, pool_radius=pool_radius
    )
