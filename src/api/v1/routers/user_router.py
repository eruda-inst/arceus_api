from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query, status
from pydantic import PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession

from .. import db, deps, models, schemas, services, utils

user_router = APIRouter(prefix="/usuarios", tags=["Usuários"])


DbDep = Annotated[AsyncSession, Depends(db.get_db)]
CurrUserDep = Annotated[models.UserModel, Depends(deps.get_curr_user)]
CreatePermDep = Annotated[
    models.UserModel, Depends(deps.has_perm(utils.PermCodes.CREATE_USER))
]
ReadPermDep = Annotated[
    models.UserModel, Depends(deps.has_perm(utils.PermCodes.READ_USER))
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
    return await services.UsuarioService.create(db=db, data=dados)


@user_router.get(path="/", summary="Obtém informações dos usuários")
async def get_all_by(
    db: DbDep,
    curr_user: CurrUserDep,
    perm: ReadPermDep,
    pagina: utils.Pagina | None = 1,
    itens_por_pagina: utils.ItensPorPagina | None = 10,
    nome: Annotated[str | None, Query(description="Filtro parcial por nome")] = None,
    email: Annotated[str | None, Query(description="Filtro parcial por e-mail")] = None,
    ativo: Annotated[bool | None, Query(description="Filtro por status")] = None,
    id_grupo: Annotated[
        int | None, Query(ge=1, description="Filtro parcial por id do grupo")
    ] = None,
) -> schemas.ListOutSchema[schemas.UserOutSchema]:
    """
    Obtém informações dos usuários
    """
    return await services.UsuarioService.get_all_by(
        db=db,
        page=pagina if pagina is not None else 1,
        items_per_page=itens_por_pagina if itens_por_pagina is not None else 10,
        name=nome,
        email=email,
        active=ativo,
        group_id=id_grupo,
    )


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
    Remove um usuário
    """
    await services.UsuarioService.del_by_id(id=id, db=db)


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
    return await services.UsuarioService.toggle_status_by_id(id=id, db=db)


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
    return await services.UsuarioService.update_pwd_by_id(
        id=id, db=db, new_pwd=nova_senha
    )
