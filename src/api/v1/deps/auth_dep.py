from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession

from .. import config, cruds, db, models, services, utils

basic_security = HTTPBasic()
bearer_security = HTTPBearer()


async def get_curr_user(
    db: Annotated[AsyncSession, Depends(db.get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_security)],
) -> models.UserModel:
    access_token = credentials.credentials
    user = await services.AuthService.verify_access_token(
        db=db, access_token=access_token
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou usuário inexistente",
        )
    return user


def get_creds(creds: Annotated[HTTPBasicCredentials, Depends(basic_security)]) -> bool:
    cred_username = creds.username
    cred_pass = creds.password

    config_username = config.settings.bot_username
    config_pass = config.settings.bot_pass.get_secret_value()

    diff_usernames = cred_username != config_username
    diff_passwords = cred_pass != config_pass

    if diff_usernames or diff_passwords:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas"
        )
    return True


def has_perm(req_perm: utils.PermCodes):
    async def dep(
        db: Annotated[AsyncSession, Depends(db.get_db)],
        current_user: Annotated[models.UserModel, Depends(get_curr_user)],
    ) -> models.UserModel:
        _, user_perms = await cruds.PermCrud.get_all_by(
            db=db,
            id_usuario=current_user.id,  # type: ignore
        )

        perm_codes = [p.codigo for p in user_perms]
        if req_perm not in perm_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão necessária: {req_perm}",
            )
        return current_user

    return dep
