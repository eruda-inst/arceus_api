from typing import Any
from . import ClienteService
from .. import utils, schemas, clients
from fastapi import HTTPException, status
from pydantic import PositiveInt, NonNegativeInt


class ComercialService:
    @staticmethod
    async def get_status_acesso(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_contrato: NonNegativeInt,
    ) -> schemas.StatusInternetOut:
        try:
            # --- Obtém contrato ---
            endpoint = "cliente_contrato"
            grid_param = [utils.Param(TB="cliente_contrato.id", P=id_contrato)]
            res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Contrato inexistente.",
                )
            contrato = regs[0]

            return schemas.StatusInternetOut(status_acesso=contrato["status_internet"])
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )

    @staticmethod
    async def get_contratos(
        protocolo: str | None,
        cnpj_cpf: str | None,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.ComercialContratoListOut:
        try:
            if not protocolo and not cnpj_cpf:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Informe protocolo ou cnpj_cpf.",
                )

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
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )

    @staticmethod
    async def post_leads(lead: schemas.LeadIn) -> schemas.LeadOut:
        try:
            # --- Cria lead ---
            endpoint = "contato"
            payload = lead.model_dump()
            """
            "data_cadastro" é obrigatório na API do IXC, porém o que é mandado é descartado, e a data é gerada automaticamente.
            """
            payload["data_cadastro"] = "N/A"
            res = await clients.IxcCliente.post(endpoint=endpoint, payload=payload)
            id = res.get("id")
            if not id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Cadastro malsucedido.",
                )

            # --- Obtém lead criado ---
            grid_param = [utils.Param(TB="contato.id", P=id)]
            res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            lead_criado = regs[0]

            return schemas.LeadOut(**lead_criado)
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )

    @staticmethod
    async def cliente_existe(cpf_cnpj: str) -> schemas.ClienteExisteOut:
        try:
            # --- Obtém cliente no Opa ---
            cpf_cnpj_limpo = utils.Formatter.only_digits(cpf_cnpj)
            endpoint = "cliente"
            filter = {"cpf_cnpj": cpf_cnpj_limpo}
            options = {"limit": 1}
            res = await clients.OpaCliente.get(
                endpoint=endpoint, filter=filter, options=options
            )
            cliente_existe = True
            data = res.get("data", [])
            if not data:
                cliente_existe = False

            return schemas.ClienteExisteOut(cliente_existe=cliente_existe)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )

    @staticmethod
    async def put_lead(cnpj_cpf: str, lead: schemas.LeadUpdate) -> schemas.LeadOut:
        try:
            # --- Obtém lead atual ---
            endpoint = "contato"
            cnpj_cpf_formatado = utils.Formatter.cnpj_cpf(cnpj_cpf)
            grid_param = [utils.Param(TB="contato.cnpj_cpf", P=cnpj_cpf_formatado)]
            res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, detail="Lead inexistente."
                )
            lead_antigo = regs[0]

            # Lead atualizado
            lead_in_data = lead.model_dump(exclude_none=True)
            lead_atualizado: dict[str, Any] = {**lead_antigo, **lead_in_data}
            del lead_atualizado["id"]

            # --- Atualiza lead ---
            endpoint = "contato"
            id = lead_antigo["id"]
            payload = lead_atualizado
            res = await clients.IxcCliente.put(
                endpoint=endpoint, id=id, payload=payload
            )
            type = res["type"]
            if type == "error":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Atualização malsucedida.",
                )

            return schemas.LeadOut(**lead_atualizado, id=id)
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )
