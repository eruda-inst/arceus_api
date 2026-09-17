from typing import Any

from fastapi import HTTPException, status

from .. import clients, schemas, utils
from . import CustomerService


class TriageService:
    @staticmethod
    async def get_customer_contact(
        protocol: str | None, cnpj_cpf: str | None
    ) -> schemas.ContactOutSchema:
        # --- Obtém cliente ---
        customer = await CustomerService.get_ixc_customer(
            protocol=protocol, cnpj_cpf=cnpj_cpf
        )

        return schemas.ContactOutSchema(telefone_celular=customer["telefone_celular"])

    @staticmethod
    async def patch_customer_contact(
        phone_number: str,
        protocol: str | None = None,
        cnpj_cpf: str | None = None,
    ) -> schemas.ContactOutSchema:
        # --- Obtém cliente atual ---
        old_customer = await CustomerService.get_ixc_customer(
            protocol=protocol, cnpj_cpf=cnpj_cpf
        )

        # Cliente atualizado
        updated_customer: dict[str, Any] = {
            **old_customer,
            "telefone_celular": utils.Formatter.cell(cell=phone_number),
        }
        del updated_customer["id"]

        # --- Atualiza cliente ---
        endpoint = f"cliente/{old_customer['id']}"
        res = await clients.IxcClient.put(endpoint=endpoint, payload=updated_customer)
        if res["type"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Atualização malsucedida",
            )

        return schemas.ContactOutSchema(telefone_celular=phone_number)
