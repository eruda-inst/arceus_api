from typing import Annotated

from fastapi import APIRouter, Depends, Path
from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from .. import db, deps, models, schemas, services

perm_router = APIRouter(prefix="/permissoes", tags=["Permissões"])

DbDep = Annotated[AsyncSession, Depends(db.get_db)]
CurrUserDep = Annotated[models.UserModel, Depends(deps.get_curr_user)]


@perm_router.get(path="/id/{id}", summary="Obtém permissão por ID")
async def get_by_id(
    db: DbDep,
    curr_user: CurrUserDep,
    id: Annotated[PositiveInt, Path(description="ID da permissão")],
) -> schemas.PermOutSchema:
    """
    Obtém informações de grupo por ID
    """
    return await services.PermService.get_by(db=db, id=id)


@perm_router.get(path="/nome/{nome}", summary="Obtém permissão por nome")
async def get_by_nome(
    db: DbDep,
    curr_user: CurrUserDep,
    nome: Annotated[str, Path(description="Nome da permissão")],
) -> schemas.PermOutSchema:
    """
    Obtém informações de grupo por nome
    """
    return await services.PermService.get_by(db=db, nome=nome)


@perm_router.get(path="/codigo/{codigo}", summary="Obtém permissão por código")
async def get_by_codigo(
    db: DbDep,
    curr_user: CurrUserDep,
    codigo: Annotated[str, Path(description="Código da permissão")],
) -> schemas.PermOutSchema:
    """
    Obtém informações de grupo por código
    """
    return await services.PermService.get_by(db=db, codigo=codigo)


@perm_router.get(path="/grupo/id/{id}", summary="Obtém permissão por ID do grupo")
async def get_by_id_grupo(
    db: DbDep,
    curr_user: CurrUserDep,
    id: Annotated[PositiveInt, Path(description="ID do grupo")],
) -> schemas.ListOutSchema[schemas.PermOutSchema]:
    """
    Obtém informações de grupos por ID do grupo
    """
    return await services.PermService.get_all_by(db=db, id_grupo=id)


@perm_router.get(path="/usuario/id/{id}", summary="Obtém permissões por ID do usuário")
async def get_by_id_usuario(
    db: DbDep,
    # curr_user: CurrUserDep,
    id: Annotated[PositiveInt, Path(description="ID do usuário")],
) -> schemas.ListOutSchema[schemas.PermOutSchema]:
    """
    Obtém informações de grupos por id do usuário
    """
    return await services.PermService.get_all_by(db=db, id_usuario=id)
