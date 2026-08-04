from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from .. import db, deps, models, schemas, services, utils

log_router = APIRouter(prefix="/logs", tags=["Logs"])

DbDep = Annotated[AsyncSession, Depends(db.get_db)]
CurrUserDep = Annotated[models.User, Depends(deps.get_curr_user)]
ReadPermDep = Annotated[models.User, Depends(deps.has_perm(utils.PermCodes.READ_LOG))]


@log_router.get(path="/", summary="Obtém informações de logs")
async def get_all(
    db: DbDep,
    # current_user: CurrUserDep,
    # perm: ReadPermDep,
    pagina: utils.Pagina | None = 1,
    itens_por_pagina: utils.ItensPorPagina | None = 10,
    metodo: Annotated[
        str | None, Query(description="Filtro parcial por método HTTP")
    ] = None,
    endpoint: Annotated[
        str | None, Query(description="Filtro parcial por endpoint")
    ] = None,
    codigo: Annotated[
        int | None, Query(ge=100, le=599, description="Filtro por código HTTP")
    ] = None,
    data_inicio: Annotated[
        str | None, Query(description="Filtro por data de início")
    ] = None,
    data_fim: Annotated[str | None, Query(description="Filtro por data de fim")] = None,
    hora_inicio: Annotated[
        str | None, Query(description="Filtro por hora de início")
    ] = None,
    hora_fim: Annotated[str | None, Query(description="Filtro por hora de fim")] = None,
    protocolo: Annotated[
        str | None, Query(description="Filtro parcial por protocolo")
    ] = None,
    setor: Annotated[str | None, Query(description="Filtro parcial por setor")] = None,
    nome_cliente: Annotated[
        str | None, Query(description="Filtro parcial por nome do cliente")
    ] = None,
) -> schemas.ListOut[schemas.LogOut]:
    """
    Obtém informações de logs
    """
    return await services.LogService.get_all(
        db=db,
        page=pagina or 1,
        items_per_page=itens_por_pagina or 10,
        metodo=metodo,
        endpoint=endpoint,
        codigo=codigo,
        data_inicio=data_inicio,
        data_fim=data_fim,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
        protocolo=protocolo,
        setor=setor,
        nome_cliente=nome_cliente,
    )
