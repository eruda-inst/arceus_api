"""
Service for sales/commercial operations (access status, leads).
"""

from typing import Any

from fastapi import HTTPException, status
from pydantic import NonNegativeInt

from .. import clients, schemas, utils


class SalesService:
    """
    Provides static methods for commercial operations.
    """

    @staticmethod
    async def get_access_status(
        # IDs NonNegativeInt, because IXC
        contract_id: NonNegativeInt,
    ) -> schemas.InternetStatusOutSchema:
        """
        Retrieve the internet access status of a contract.

        Args:
            contract_id: Contract ID in IXC.

        Returns:
            InternetStatusOutSchema with the access status.

        Raises:
            HTTPException: 404 if the contract does not exist.
        """
        # --- Get contract ---
        endpoint = "cliente_contrato"
        grid_param = [utils.Param(TB="cliente_contrato.id", P=contract_id)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contrato inexistente",
            )
        contract = regs[0]

        return schemas.InternetStatusOutSchema(
            status_acesso=contract["status_internet"]
        )

    @staticmethod
    async def post_leads(lead: schemas.LeadInSchema) -> schemas.LeadOutSchema:
        """
        Create a new lead in IXC.

        Args:
            lead: Lead input data.

        Returns:
            LeadOutSchema with the created lead.

        Raises:
            HTTPException: 500 if creation fails.
        """
        # --- Post lead ---
        endpoint = "contato"
        payload = lead.model_dump()
        """
        "data_cadastro" é obrigatório na API do IXC, porém o que é mandado é descartado, e a data é gerada automaticamente
        """
        payload["data_cadastro"] = "N/A"
        res = await clients.IxcClient.post(endpoint=endpoint, payload=payload)
        if not (id := res.get("id")):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cadastro malsucedido",
            )

        # --- Get lead ---
        grid_param = [utils.Param(TB="contato.id", P=id)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        regs = res.get("registros", [])
        created_lead = regs[0]

        return schemas.LeadOutSchema(**created_lead)

    @staticmethod
    async def patch_lead(
        cnpj_cpf: str, lead: schemas.LeadUpdateSchema
    ) -> schemas.LeadOutSchema:
        """
        Partially update a lead identified by CNPJ/CPF.

        Args:
            cnpj_cpf: Document that identifies the lead.
            lead: Partial lead data to update.

        Returns:
            LeadOutSchema with the updated lead.

        Raises:
            HTTPException: 404 if the lead does not exist.
            HTTPException: 500 if the update fails.
        """
        # --- Get lead ---
        endpoint = "contato"
        formatted_cnpj_cpf = utils.Formatter.cnpj_cpf(cnpj_cpf)
        grid_param = [utils.Param(TB="contato.cnpj_cpf", P=formatted_cnpj_cpf)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Lead inexistente")
        old_lead = regs[0]

        lead_in_data = lead.model_dump(exclude_none=True)
        updated_lead: dict[str, Any] = {**old_lead, **lead_in_data}
        del updated_lead["id"]

        # --- Put lead ---
        id = old_lead["id"]
        endpoint = f"contato/{id}"
        payload = updated_lead
        res = await clients.IxcClient.put(endpoint=endpoint, payload=payload)
        if res["type"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Atualização malsucedida",
            )

        return schemas.LeadOutSchema(**updated_lead, id=id)
