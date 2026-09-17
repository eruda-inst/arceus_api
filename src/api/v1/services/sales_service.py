from typing import Any

from fastapi import HTTPException, status
from pydantic import NonNegativeInt

from .. import clients, schemas, utils


class SalesService:
    @staticmethod
    async def get_access_status(
        # IDs NonNegativeInt, pois o IXC é quebrado
        contract_id: NonNegativeInt,
    ) -> schemas.InternetStatusOutSchema:
        # --- Obtém contrato ---
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
        # --- Cria lead ---
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

        # --- Obtém lead criado ---
        grid_param = [utils.Param(TB="contato.id", P=id)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        regs = res.get("registros", [])
        created_lead = regs[0]

        return schemas.LeadOutSchema(**created_lead)

    @staticmethod
    async def patch_lead(
        cnpj_cpf: str, lead: schemas.LeadUpdateSchema
    ) -> schemas.LeadOutSchema:
        # --- Obtém lead atual ---
        endpoint = "contato"
        formatted_cnpj_cpf = utils.Formatter.cnpj_cpf(cnpj_cpf)
        grid_param = [utils.Param(TB="contato.cnpj_cpf", P=formatted_cnpj_cpf)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Lead inexistente")
        old_lead = regs[0]

        # Lead atualizado
        lead_in_data = lead.model_dump(exclude_none=True)
        updated_lead: dict[str, Any] = {**old_lead, **lead_in_data}
        del updated_lead["id"]

        # --- Atualiza lead ---
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
