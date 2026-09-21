"""
Router for permission-related endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Path
from pydantic import PositiveInt

from .. import cruds, schemas, utils

perm_router = APIRouter(prefix="/permissoes", tags=["Permissões"])


@perm_router.get(path="/id/{id}", summary="Obtém permissão por ID")
async def get_by_id(
    db: utils.DbDep,
    id: Annotated[PositiveInt, Path(description="ID da permissão")],
) -> schemas.PermOutSchema:
    """
    Obtém informações de grupo por ID
    """
    perm = await cruds.PermCrud.get_by(db=db, id=id)
    return schemas.PermOutSchema.model_validate(perm)


@perm_router.get(path="/nome/{nome}", summary="Obtém permissão por nome")
async def get_by_name(
    db: utils.DbDep,
    nome: Annotated[str, Path(description="Nome da permissão")],
) -> schemas.PermOutSchema:
    """
    Obtém informações de grupo por nome
    """
    perm = await cruds.PermCrud.get_by(db=db, name=nome)
    return schemas.PermOutSchema.model_validate(perm)


@perm_router.get(path="/codigo/{codigo}", summary="Obtém permissão por código")
async def get_by_code(
    db: utils.DbDep,
    codigo: Annotated[str, Path(description="Código da permissão")],
) -> schemas.PermOutSchema:
    """
    Obtém informações de grupo por código
    """
    perm = await cruds.PermCrud.get_by(db=db, code=codigo)
    return schemas.PermOutSchema.model_validate(perm)


@perm_router.get(path="/grupo/id/{id}", summary="Obtém permissão por ID do grupo")
async def get_by_group_id(
    db: utils.DbDep,
    id: Annotated[PositiveInt, Path(description="ID do grupo")],
) -> schemas.ListOutSchema[schemas.PermOutSchema]:
    """
    Obtém informações de grupos por ID do grupo
    """
    total_items, perms = await cruds.PermCrud.get_all_by(db=db, group_id=id)

    return schemas.ListOutSchema[schemas.PermOutSchema](
        data=[schemas.PermOutSchema.model_validate(p) for p in perms],
        meta=schemas.MetaOutSchema(
            itens_por_pagina=10, total_itens=total_items, pagina_atual=1
        ),
    )


@perm_router.get(path="/usuario/id/{id}", summary="Obtém permissões por ID do usuário")
async def get_by_user_id(
    db: utils.DbDep,
    id: Annotated[PositiveInt, Path(description="ID do usuário")],
) -> schemas.ListOutSchema[schemas.PermOutSchema]:
    """
    Obtém informações de grupos por id do usuário
    """
    total_items, perms = await cruds.PermCrud.get_all_by(db=db, user_id=id)

    return schemas.ListOutSchema[schemas.PermOutSchema](
        data=[schemas.PermOutSchema.model_validate(p) for p in perms],
        meta=schemas.MetaOutSchema(
            itens_por_pagina=10, total_itens=total_items, pagina_atual=1
        ),
    )
