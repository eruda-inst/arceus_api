from typing import Annotated
from .. import services, schemas
from fastapi import APIRouter, Query

vila_router = APIRouter(prefix="/vila", tags=["Vila"])


@vila_router.get(
    path="/status_conexao", summary="Obtém status de conexão de um cliente."
)
async def get_status_conexao(
    numero_residencia: Annotated[int, Query(ge=1, description="Número de residência.")],
) -> schemas.StatusConexaoOut:
    """
    Obtém status de conexão de um cliente, através do número de residência.
    """
    return await services.VilaService.get_status_conexao(
        numero_residencia=numero_residencia
    )
