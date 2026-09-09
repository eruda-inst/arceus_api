from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .. import config, db, models, services

basic_security = HTTPBasic()

bearer_security = HTTPBearer()


async def get_curr_user(
    db: Annotated[AsyncSession, Depends(db.get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_security)],
) -> models.UserModel:
    access_token = credentials.credentials
    user = await services.AuthenticationService.verify_access_token(
        db=db, access_token=access_token
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou usuário inexistente",
        )
    return user


def get_creds(creds: Annotated[HTTPBasicCredentials, Depends(basic_security)]) -> bool:
    if (
        creds.username != config.settings.bot_username
        or creds.password != config.settings.bot_pass.get_secret_value()
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True
