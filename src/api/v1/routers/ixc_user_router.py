"""
Router for IXC user-related endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from .. import deps, models, schemas, services, utils

ixc_user_router = APIRouter(prefix="/usuarios-ixc", tags=["Usuários IXC"])


# Dependency alias for the current user
curr_user_dep = Annotated[models.UserModel, Depends(deps.get_curr_user)]


@ixc_user_router.get(path="/", summary="Obtém informações de usuários")
async def get_all(
    _: curr_user_dep,
    pagina: utils.Page = 1,
    itens_por_pagina: utils.ItemsPerPage = 10,
    nome: Annotated[str | None, Query(description="Filtro parcial por nome")] = None,
    email: Annotated[str | None, Query(description="Filtro parcial por e-mail")] = None,
) -> schemas.ListOutSchema[schemas.IXCUserOutSchema]:
    """
    Obtém informações de usuários do IXC
    """
    return await services.IXCUserService.get_all(
        page=pagina, items_per_page=itens_por_pagina, name=nome, email=email
    )
