from typing import Annotated

from fastapi import APIRouter, Depends, Query

from .. import deps, models, schemas, services, utils

ixc_user_router = APIRouter(prefix="/usuarios-ixc", tags=["Usuários IXC"])


current_user_dep = Annotated[models.UserModel, Depends(deps.get_curr_user)]


@ixc_user_router.get(path="/", summary="Obtém informações de usuários")
async def get_all(
    current_user: current_user_dep,
    pagina: utils.Pagina | None = 1,
    itens_por_pagina: utils.ItensPorPagina | None = 10,
    nome: Annotated[str | None, Query(description="Filtro parcial por nome")] = None,
    email: Annotated[str | None, Query(description="Filtro parcial por e-mail")] = None,
) -> schemas.ListOutSchema[schemas.IXCUsuarioOutSchema]:
    """
    Obtém informações de usuários do IXC
    """
    return await services.IXCUserService.get_all(
        page=pagina or 1, items_per_page=itens_por_pagina or 10, name=nome, email=email
    )
