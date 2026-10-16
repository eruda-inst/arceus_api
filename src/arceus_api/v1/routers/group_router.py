"""
Router for group-related endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Path
from pydantic import PositiveInt

from .. import cruds, schemas, utils

group_router = APIRouter(prefix="/grupos", tags=["Grupos"])


@group_router.get(path="/", summary="Obtém grupos")
async def get_all(db: utils.DbDep) -> schemas.ListOutSchema[schemas.GroupOutSchema]:
    """
    Obtém informações de grupos
    """
    total_items, groups = await cruds.GroupCrud.get_all(db=db)

    return schemas.ListOutSchema[schemas.GroupOutSchema](
        data=[schemas.GroupOutSchema.model_validate(g) for g in groups],
        meta=schemas.MetaOutSchema(
            pagina_atual=1,
            itens_por_pagina=10,
            total_itens=total_items,
        ),
    )


@group_router.get(path="/id/{id}", summary="Obtém grupo por ID")
async def get_by_id(
    db: utils.DbDep,
    id: Annotated[PositiveInt, Path(description="ID do grupo")],
) -> schemas.GroupOutSchema:
    """
    Obtém informações de grupo por ID
    """
    group = await cruds.GroupCrud.get_by(db=db, id=id)
    return schemas.GroupOutSchema.model_validate(group)


@group_router.get(path="/nome/{nome}", summary="Obtém grupo por nome")
async def get_by_name(
    db: utils.DbDep,
    nome: Annotated[str, Path(description="Nome do grupo")],
) -> schemas.GroupOutSchema:
    """
    Obtém informações de grupo por nome
    """
    group = await cruds.GroupCrud.get_by(db=db, name=nome)
    return schemas.GroupOutSchema.model_validate(group)


@group_router.get(path="/usuario/id/{id}", summary="Obtém grupo por ID do usuário")
async def get_by_user_id(
    db: utils.DbDep,
    id: Annotated[PositiveInt, Path(description="ID do usuário")],
) -> schemas.GroupOutSchema:
    """
    Obtém informações de grupo por id do usuário
    """
    group = await cruds.GroupCrud.get_by(db=db, user_id=id)
    return schemas.GroupOutSchema.model_validate(group)
