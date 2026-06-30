from typing import Annotated
from .. import services, schemas
from fastapi import APIRouter, Query

vila_router = APIRouter(prefix="/vila", tags=["Vila"])

NumeroResidencia = Annotated[int, Query(ge=1, description="Número de residência.")]


@vila_router.get(
    path="/status_conexao", summary="Obtém status da conexão de um cliente."
)
async def get_status_conexao(
    numero_residencia: NumeroResidencia,
) -> schemas.NewStatusConexaoOut:
    """
    Obtém status da conexão de um cliente, através do número de residência.
    """
    return await services.VilaService.get_status_conexao(
        numero_residencia=numero_residencia
    )


@vila_router.get(path="/status_onu", summary="Obtém status da ONU de um cliente.")
async def get_status_onu(numero_residencia: NumeroResidencia):
    """
    Obtém status da ONU de um cliente, através do número de residência.
    """
    return await services.VilaService.get_status_onu(
        numero_residencia=numero_residencia
    )
