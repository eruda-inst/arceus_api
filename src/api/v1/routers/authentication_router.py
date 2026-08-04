from typing import Annotated

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .. import db, deps, models, schemas, services

authentication_router = APIRouter(prefix="/autenticacao", tags=["Autenticação"])

db_dep = Annotated[AsyncSession, Depends(dependency=db.get_db)]


@authentication_router.post(path="/login", summary="Autenticação de usuário")
async def login(
    db: db_dep,
    user: Annotated[schemas.UserLogin, Body(description="Credenciais de login")],
) -> schemas.AccessTokenOut:
    """
    Autenticação de usuário para acessar o sistema
    """
    return await services.AuthenticationService.login(user=user, db=db)


@authentication_router.post(path="/refresh-token", summary="Renova token")
async def refresh_token(
    db: db_dep,
    refresh_token: Annotated[
        schemas.RefreshTokenIn, Body(description="Token de atualização")
    ],
) -> schemas.AccessTokenOut:
    """
    Renova token de acesso
    """
    return await services.AuthenticationService.refresh_token(
        refresh_token=refresh_token, db=db
    )


@authentication_router.get(path="/me", summary="Usuário atual")
async def me(
    db: db_dep,
    current_user: Annotated[models.User, Depends(dependency=deps.get_curr_user)],
) -> schemas.UserOut:
    """
    Usuário atual logado
    """
    return schemas.UserOut.model_validate(obj=current_user)
