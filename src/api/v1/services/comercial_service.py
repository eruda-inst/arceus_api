from typing import Any

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt

from .. import clients, schemas, utils
from . import ClienteService


class ComercialService:
    @staticmethod
    async def get_status_acesso(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_contrato: NonNegativeInt,
    ) -> schemas.StatusInternetOut:
        # --- Obtém contrato ---
        endpoint = "cliente_contrato"
        grid_param = [utils.Param(TB="cliente_contrato.id", P=id_contrato)]
        res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contrato inexistente",
            )
        contrato = regs[0]

        return schemas.StatusInternetOut(status_acesso=contrato["status_internet"])

    @staticmethod
    async def get_contratos(
        protocolo: str | None,
        cnpj_cpf: str | None,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.ComercialContratoListOut:
        # --- Obtém contratos ativos ---
        contratos = await ClienteService.get_contratos_ativos(
            protocolo=protocolo,
            cnpj_cpf=cnpj_cpf,
            pagina=pagina,
            itens_por_pagina=itens_por_pagina,
        )

        return schemas.ComercialContratoListOut(
            data=[schemas.ComercialContratoOut(**c) for c in contratos],
            meta=schemas.Meta(
                total_itens=len(contratos),
                pagina_atual=pagina,
                itens_por_pagina=itens_por_pagina,
            ),
        )

    @staticmethod
    async def post_leads(lead: schemas.LeadIn) -> schemas.LeadOut:
        # --- Cria lead ---
        endpoint = "contato"
        payload = lead.model_dump()
        """
        "data_cadastro" é obrigatório na API do IXC, porém o que é mandado é descartado, e a data é gerada automaticamente
        """
        payload["data_cadastro"] = "N/A"
        res = await clients.IxcCliente.post(endpoint=endpoint, payload=payload)
        if not (id := res.get("id")):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cadastro malsucedido",
            )

        # --- Obtém lead criado ---
        grid_param = [utils.Param(TB="contato.id", P=id)]
        res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
        regs = res.get("registros", [])
        lead_criado = regs[0]

        return schemas.LeadOut(**lead_criado)

    @staticmethod
    async def cliente_existe(cpf_cnpj: str) -> schemas.ClienteExisteOut:
        # --- Obtém cliente no Opa ---
        cpf_cnpj_limpo = utils.Formatter.only_digits(cpf_cnpj)
        endpoint = "cliente"
        filter = {"cpf_cnpj": cpf_cnpj_limpo}
        options = {"limit": 1}
        res = await clients.OpaCliente.get(
            endpoint=endpoint, filter=filter, options=options
        )
        cliente_existe = True
        if not (_ := res.get("data", [])):
            cliente_existe = False

        return schemas.ClienteExisteOut(cliente_existe=cliente_existe)

    @staticmethod
    async def put_lead(cnpj_cpf: str, lead: schemas.LeadUpdate) -> schemas.LeadOut:
        # --- Obtém lead atual ---
        endpoint = "contato"
        cnpj_cpf_formatado = utils.Formatter.cnpj_cpf(cnpj_cpf)
        grid_param = [utils.Param(TB="contato.cnpj_cpf", P=cnpj_cpf_formatado)]
        res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Lead inexistente")
        lead_antigo = regs[0]

        # Lead atualizado
        lead_in_data = lead.model_dump(exclude_none=True)
        lead_atualizado: dict[str, Any] = {**lead_antigo, **lead_in_data}
        del lead_atualizado["id"]

        # --- Atualiza lead ---
        endpoint = "contato"
        id = lead_antigo["id"]
        payload = lead_atualizado
        res = await clients.IxcCliente.put(endpoint=endpoint, id=id, payload=payload)
        if res["type"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Atualização malsucedida",
            )

        return schemas.LeadOut(**lead_atualizado, id=id)
