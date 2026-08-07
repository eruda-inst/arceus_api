from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .. import db, models, services

security = HTTPBearer()


async def get_curr_user(
    db: Annotated[AsyncSession, Depends(db.get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> models.User:
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
