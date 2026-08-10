from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, db, models, utils
from .authentication_dep import get_curr_user


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
