from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from .. import cruds, db, deps, models, schemas, services, utils

user_router = APIRouter(prefix="/usuarios", tags=["Usuários"])


DbDep = Annotated[AsyncSession, Depends(db.get_db)]
CurrUserDep = Annotated[models.UserModel, Depends(deps.get_curr_user)]
CreatePermDep = Annotated[
    models.UserModel, Depends(deps.has_perm(utils.PermCodes.CREATE_USER))
]
UpdatePermDep = Annotated[
    models.UserModel, Depends(deps.has_perm(utils.PermCodes.UPDATE_USER))
]
DelPermDep = Annotated[
    models.UserModel, Depends(deps.has_perm(utils.PermCodes.DEL_USER))
]


@user_router.post(
    path="/", status_code=status.HTTP_201_CREATED, summary="Cadastra um novo usuário"
)
async def create(
    db: DbDep,
    curr_user: CurrUserDep,
    perm: CreatePermDep,
    dados: Annotated[schemas.UserInSchema, Body(description="Dados do novo usuário")],
) -> schemas.UserOutSchema:
    """
    Cadastra um novo usuário
    """
    # Only users that exist in the external IXC system are allowed to be created locally.
    # If get_by_email() does not find the user, it raises a "not found" exception,
    # which prevents the local user from being created.
    _ = await services.IXCUserService.get_by_email(email=dados.email)
    created_user = await cruds.UserCrud.create(db=db, data=dados)
    return schemas.UserOutSchema.model_validate(created_user)


@user_router.delete(
    path="/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove um usuário"
)
async def del_by_id(
    db: DbDep,
    curr_user: CurrUserDep,
    perm: DelPermDep,
    id: PositiveInt,
) -> None:
    """
    Remove um usuário pelo ID
    """
    await cruds.UserCrud.del_by_id(db=db, id=id)


@user_router.patch(
    path="/{id}/alternar-status", summary="Alterna o status de um usuário"
)
async def toggle_status_by_id(
    db: DbDep,
    curr_user: CurrUserDep,
    perm: UpdatePermDep,
    id: PositiveInt,
) -> schemas.UserOutSchema:
    """
    Alterna o status do usuário, i.e., se estiver ativo, fica inativo, e vice-versa
    """
    updated_user = await cruds.UserCrud.toggle_status_by_id(db=db, id=id)
    return schemas.UserOutSchema.model_validate(updated_user)


@user_router.patch(path="/mudar-senha/id/{id}", summary="Atualiza senha de um usuário")
async def update_pwd_by_id(
    db: DbDep,
    curr_user: CurrUserDep,
    perm: UpdatePermDep,
    id: PositiveInt,
    nova_senha: Annotated[
        str,
        Body(embed=True, description="Nova senha", min_length=8, examples=["12345678"]),
    ],
) -> schemas.UserOutSchema:
    """
    Atualiza senha de um usuário
    """
    updated_user = await cruds.UserCrud.update_pwd_by_id(
        db=db, id=id, new_pwd=nova_senha
    )
    return schemas.UserOutSchema.model_validate(updated_user)
