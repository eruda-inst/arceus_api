from typing import Annotated

from fastapi import APIRouter, Body, Query

from .. import schemas, services

vila_router = APIRouter(prefix="/vila", tags=["Vila"])

NumeroResidencia = Annotated[int, Query(ge=1, description="Número da residência")]
Ppoe = Annotated[str, Query(description="PPOE associado ao cliente")]


@vila_router.get(path="/contrato", summary="Obtém contrato de um cliente")
async def get_contrato(
    numero_residencia: NumeroResidencia | None = None, ppoe: Ppoe | None = None
) -> schemas.VilaContratoOutSchema:
    """
    Obtém contrato de um cliente, através do número da residência
    """
    return await services.VilaService.get_contrato(
        numero_residencia=numero_residencia, ppoe=ppoe
    )


@vila_router.get(
    path="/status-conexao", summary="Obtém status da conexão de um cliente"
)
async def get_status_conexao(
    numero_residencia: NumeroResidencia | None = None, ppoe: Ppoe | None = None
) -> schemas.StatusConexaoOutSchema:
    """
    Obtém status da conexão de um cliente, através do número da residência
    """
    return await services.VilaService.get_status_conexao(
        numero_residencia=numero_residencia, ppoe=ppoe
    )


@vila_router.get(path="/status-onu", summary="Obtém status da ONU de um cliente")
async def get_status_onu(
    numero_residencia: NumeroResidencia | None = None, ppoe: Ppoe | None = None
) -> schemas.StatusOnuOutSchema:
    """
    Obtém status da ONU de um cliente, através do número da residência
    """
    return await services.VilaService.get_status_onu(
        numero_residencia=numero_residencia, ppoe=ppoe
    )


@vila_router.get(
    path="/atendimentos", summary="Obtém atendimentos abertos de um cliente"
)
async def get_atendimentos(
    numero_residencia: NumeroResidencia | None = None,
    ppoe: Ppoe | None = None,
    pagina: Annotated[int | None, Query(ge=1, description="Número da página")] = 1,
    itens_por_pagina: Annotated[
        int | None, Query(ge=1, description="Itens por página")
    ] = 10,
) -> schemas.ListOutSchema[schemas.AtendimentoOutSchema]:
    """
    Obtém atendimentos abertos de um cliente, através do número da residência
    """
    return await services.VilaService.get_atendimentos(
        numero_residencia=numero_residencia,
        ppoe=ppoe,
        pagina=pagina,
        itens_por_pagina=itens_por_pagina,
    )


@vila_router.post(path="/limpar-mac", summary="Limpa MAC Address de um cliente")
async def post_limpar_mac(
    numero_residencia: NumeroResidencia | None = None, ppoe: Ppoe | None = None
) -> schemas.MensagemOutSchema:
    """
    Limpa MAC Address de um cliente, através do número da residência
    """
    return await services.VilaService.post_limpar_mac(
        numero_residencia=numero_residencia, ppoe=ppoe
    )


@vila_router.post(path="/desconectar-cliente", summary="Desconecta um cliente")
async def post_desconectar_cliente(
    numero_residencia: NumeroResidencia | None = None, ppoe: Ppoe | None = None
) -> schemas.MensagemOutSchema:
    """
    Desconecta um cliente, através do número da residência
    """
    return await services.VilaService.post_desconectar_cliente(
        numero_residencia=numero_residencia, ppoe=ppoe
    )


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
