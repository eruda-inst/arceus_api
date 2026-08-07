from typing import Annotated

from fastapi import APIRouter, Depends, Path
from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from .. import db, deps, models, schemas, services

group_router = APIRouter(prefix="/grupos", tags=["Grupos"])

DbDep = Annotated[AsyncSession, Depends(dependency=db.get_db)]
CurrUserDep = Annotated[models.User, Depends(dependency=deps.get_curr_user)]


@group_router.get(path="/", summary="Obtém grupos")
async def get_all(
    db: DbDep, curr_user: CurrUserDep
) -> schemas.ListOut[schemas.GroupOut]:
    """
    Obtém informações de grupos
    """
    return await services.GroupService.get_all(db=db)


@group_router.get(path="/id/{id}", summary="Obtém grupo por ID")
async def get_by_id(
    db: DbDep,
    curr_user: CurrUserDep,
    id: Annotated[PositiveInt, Path(description="ID do grupo")],
) -> schemas.GroupOut:
    """
    Obtém informações de grupo por ID
    """
    return await services.GroupService.get_by(db=db, id=id)


@group_router.get(path="/nome/{nome}", summary="Obtém grupo por nome")
async def get_by_name(
    db: DbDep,
    curr_user: CurrUserDep,
    nome: Annotated[str, Path(description="Nome do grupo")],
) -> schemas.GroupOut:
    """
    Obtém informações de grupo por nome
    """
    return await services.GroupService.get_by(db=db, nome=nome)


@group_router.get(path="/usuario/id/{id}", summary="Obtém grupo por ID do usuário")
async def get_by_user_id(
    db: DbDep,
    curr_user: CurrUserDep,
    id: Annotated[PositiveInt, Path(description="ID do usuário")],
) -> schemas.GroupOut:
    """
    Obtém informações de grupo por id do usuário
    """
    return await services.GroupService.get_by(db=db, id_usuario=id)
