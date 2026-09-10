from typing import Annotated

from fastapi import APIRouter, Depends, Path
from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, db, deps, models, schemas

group_router = APIRouter(prefix="/grupos", tags=["Grupos"])

DbDep = Annotated[AsyncSession, Depends(dependency=db.get_db)]
CurrUserDep = Annotated[models.UserModel, Depends(dependency=deps.get_curr_user)]


@group_router.get(path="/", summary="Obtém grupos")
async def get_all(
    db: DbDep,
    # _: CurrUserDep
) -> schemas.ListOutSchema[schemas.GroupOutSchema]:
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
    db: DbDep,
    # _: CurrUserDep,
    id: Annotated[PositiveInt, Path(description="ID do grupo")],
) -> schemas.GroupOutSchema:
    """
    Obtém informações de grupo por ID
    """
    group = await cruds.GroupCrud.get_by(db=db, id=id)
    return schemas.GroupOutSchema.model_validate(group)


@group_router.get(path="/nome/{nome}", summary="Obtém grupo por nome")
async def get_by_name(
    db: DbDep,
    _: CurrUserDep,
    nome: Annotated[str, Path(description="Nome do grupo")],
) -> schemas.GroupOutSchema:
    """
    Obtém informações de grupo por nome
    """
    group = await cruds.GroupCrud.get_by(db=db, nome=nome)
    return schemas.GroupOutSchema.model_validate(group)


@group_router.get(path="/usuario/id/{id}", summary="Obtém grupo por ID do usuário")
async def get_by_user_id(
    db: DbDep,
    _: CurrUserDep,
    id: Annotated[PositiveInt, Path(description="ID do usuário")],
) -> schemas.GroupOutSchema:
    """
    Obtém informações de grupo por id do usuário
    """
    group = await cruds.GroupCrud.get_by(db=db, id_usuario=id)
    return schemas.GroupOutSchema.model_validate(group)
