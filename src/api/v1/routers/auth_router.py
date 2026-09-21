"""
Router for authentication endpoints.

Provides login, logout, token refresh, and current user retrieval.
"""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import db, deps, models, schemas, services

auth_router = APIRouter(prefix="/autenticacao", tags=["Autenticação"])

# Dependency aliases
DbDep = Annotated[AsyncSession, Depends(dependency=db.get_db)]
CurrUserDep = Annotated[models.UserModel, Depends(dependency=deps.get_curr_user)]


@auth_router.post(path="/login", summary="Autenticação de usuário")
async def login(
    db: DbDep,
    user: Annotated[schemas.UserLoginSchema, Body(description="Credenciais de login")],
) -> schemas.AccessTokenOutSchema:
    """
    Autenticação de usuário para acessar o sistema
    """
    return await services.AuthService.login(user=user, db=db)


@auth_router.post(
    path="/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Realiza logout do usuário",
)
async def logout(curr_user: CurrUserDep, db: DbDep) -> None:
    """
    Invalida token de usuário autenticado
    """
    # Increment the token version to invalidate all existing tokens for this user
    curr_user.versao_token += 1  # type: ignore
    await db.commit()


@auth_router.post(path="/refresh-token", summary="Renova token")
async def refresh(
    db: DbDep,
    refresh_token: Annotated[
        str, Body(embed=True, description="Token de atualização", examples=["eyJ..."])
    ],
) -> schemas.AccessTokenOutSchema:
    """
    Renova token de acesso
    """
    return await services.AuthService.refresh_token(refresh_token=refresh_token, db=db)


@auth_router.get(path="/me", summary="Usuário atual")
async def me(_: DbDep, curr_user: CurrUserDep) -> schemas.UserOutSchema:
    """
    Usuário atual logado
    """
    return schemas.UserOutSchema.model_validate(curr_user)
