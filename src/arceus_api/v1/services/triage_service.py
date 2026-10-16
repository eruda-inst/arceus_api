"""
Service for triage operations (customer contact info).
"""

from typing import Any

from fastapi import HTTPException, status

from .. import clients, schemas, services, utils


class TriageService:
    """
    Provides static methods for triage operations.
    """

    @staticmethod
    async def get_customer_contact(
        protocol: str | None, cnpj_cpf: str | None
    ) -> schemas.ContactOutSchema:
        """
        Retrieve the contact information for a customer.

        Args:
            protocol: OPA protocol.
            cnpj_cpf: Customer document.

        Returns:
            ContactOutSchema with the customer's cellphone number.
        """
        # --- Get customer ---
        customer = await services.CustomerService.get_ixc_customer(
            protocol=protocol, cnpj_cpf=cnpj_cpf
        )

        return schemas.ContactOutSchema(telefone_celular=customer["telefone_celular"])

    @staticmethod
    async def patch_customer_contact(
        phone_number: str,
        protocol: str | None = None,
        cnpj_cpf: str | None = None,
    ) -> schemas.ContactOutSchema:
        """
        Update the contact phone number for a customer.

        Args:
            phone_number: New phone number.
            protocol: OPA protocol.
            cnpj_cpf: Customer document.

        Returns:
            ContactOutSchema with the updated phone number.

        Raises:
            HTTPException: 500 if the update fails.
        """
        # --- Get customer ---
        old_customer = await services.CustomerService.get_ixc_customer(
            protocol=protocol, cnpj_cpf=cnpj_cpf
        )

        updated_customer: dict[str, Any] = {
            **old_customer,
            "telefone_celular": utils.Formatter.cell(cell=phone_number),
        }
        del updated_customer["id"]

        # --- Put customer ---
        endpoint = f"cliente/{old_customer['id']}"
        res = await clients.IxcClient.put(endpoint=endpoint, payload=updated_customer)
        if res["type"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Atualização malsucedida",
            )

        return schemas.ContactOutSchema(telefone_celular=phone_number)
