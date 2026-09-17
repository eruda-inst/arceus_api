"""
Service for IXC user-related operations.
"""

from fastapi import HTTPException, status
from pydantic import EmailStr, PositiveInt

from .. import clients, schemas, utils


class IXCUserService:
    """
    Provides class/static methods for IXC user operations.
    """

    @classmethod
    async def get_all(
        cls,
        page: PositiveInt,
        items_per_page: PositiveInt,
        name: str | None = None,
        email: str | None = None,
    ) -> schemas.ListOutSchema[schemas.IXCUserOutSchema]:
        """
        Retrieve a paginated list of active IXC users.

        Args:
            page: Page number.
            items_per_page: Items per page.
            name: Optional partial name filter.
            email: Optional partial email filter.

        Returns:
            A ListOutSchema of IXCUserOutSchema.
        """
        endpoint = "usuarios"
        grid_param = [utils.Param(TB="usuarios.status", P="A")]

        if name is not None:
            grid_param.append(utils.Param(TB="usuarios.nome", OP="L", P=name))
        if email is not None:
            grid_param.append(utils.Param(TB="usuarios.email", OP="L", P=email))

        res = await clients.IxcClient.get(
            endpoint=endpoint,
            grid_param=grid_param,
            pagina=page,
            itens_por_pagina=items_per_page,
        )
        ixc_users = res.get("registros", [])
        total_items = res.get("total", 0)
        total_items = int(total_items)

        return schemas.ListOutSchema[schemas.IXCUserOutSchema](
            data=[schemas.IXCUserOutSchema.model_validate(i) for i in ixc_users],
            meta=schemas.MetaOutSchema(
                itens_por_pagina=items_per_page,
                pagina_atual=page,
                total_itens=total_items,
            ),
        )

    @staticmethod
    async def get_by_email(email: EmailStr) -> schemas.IXCUserOutSchema:
        """
        Retrieve an active IXC user by email.

        Args:
            email: User email.

        Returns:
            The matching IXCUserOutSchema.

        Raises:
            HTTPException: 404 if no active user is found with the given email.
        """
        endpoint = "usuarios"
        grid_param = [
            utils.Param(TB="usuarios.status", P="A"),
            utils.Param(TB="usuarios.email", P=email),
        ]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário IXC inexistente",
            )
        user = regs[0]
        return schemas.IXCUserOutSchema.model_validate(user)
