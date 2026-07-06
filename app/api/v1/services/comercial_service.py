from typing import Any
from . import service_service
from pydantic import PositiveInt
from fastapi import HTTPException, status
from .. import utils, schemas, clients, services


class ComercialService(service_service.Service):
    @staticmethod
    async def get_status_acesso(id_contrato: PositiveInt) -> schemas.StatusInternetOut:
        try:
            # --- Contrato ---
            endpoint = "cliente_contrato"
            grid_param = [
                {"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}
            ]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Contrato não encontrado.",
                )
            contrato = regs[0]
            return schemas.StatusInternetOut(status_acesso=contrato["status_internet"])
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {e}",
            )

    @classmethod
    async def get_contratos(
        cls,
        protocolo: str | None,
        cnpj_cpf: str | None,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.ComercialContratoListOut:
        try:
            # --- Cliente ---
            id_cliente = await cls.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )
            res = await clients.IXCCliente.get_cliente_ixc(id=id_cliente)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Nenum cliente encontrado.",
                )
            cliente = regs[0]

            # --- Contratos ---
            endpoint = "cliente_contrato"
            grid_param = [
                {"TB": "cliente_contrato.id_cliente", "OP": "=", "P": str(id_cliente)},
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "I"},
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "N"},
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "D"},
            ]
            res = await clients.IXCCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )
            regs = res.get("registros", [])
            total = res.get("total", 0)
            contratos = regs

            contratos_parciais: list[schemas.ComercialContrato] = []

            # --- Iteração entre contratos ---
            for contrato in contratos:
                id_contrato = contrato.get("id")

                # --- Login ---
                endpoint = "radusuarios"
                grid_param = [
                    {"TB": "radusuarios.id_contrato", "OP": "=", "P": str(id_contrato)}
                ]
                res = await clients.IXCCliente.get(
                    endpoint=endpoint, grid_param=grid_param
                )
                regs = res.get("registros", [])
                if not regs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Nenhum login encontrado.",
                    )
                login = regs[0]

                # --- Fatura referência ---
                fatura_referencia: dict[str, Any] | None = (
                    await services.FinanceiroService.get_fatura_referencia(
                        id_contrato=id_contrato
                    )
                )

                if not fatura_referencia:
                    fatura_referencia = {"valor": 0.00, "data_vencimento": ""}

                # --- Contrato parcial ---
                contratos_parciais.append(
                    schemas.ComercialContrato(
                        id=id_contrato,
                        contrato=contrato.get("contrato"),
                        nome_cliente=cliente.get("razao"),
                        valor=fatura_referencia["valor"],
                        status_acesso=contrato.get("status_internet"),
                        data_vencimento=fatura_referencia["data_vencimento"],
                        id_cliente=id_cliente,
                        id_login=login.get("id"),
                    )
                )

            return schemas.ComercialContratoListOut(
                data=contratos_parciais,
                meta=schemas.Meta(
                    total_itens=total,
                    pagina_atual=pagina,
                    itens_por_pagina=itens_por_pagina,
                ),
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {e}",
            )

    @staticmethod
    async def post_leads(lead: schemas.LeadIn) -> schemas.LeadCreate:
        try:
            # --- Lead ---
            endpoint = "contato"
            payload = lead.model_dump()
            """
            "data_cadastro" é obrigatório na API do IXC, porém o que é mandado é descartado, e a data é gerada automaticamente pela própria API deles.
            """
            payload["data_cadastro"] = "N/A"
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)
            id_lead = res.get("id", None)
            if not id_lead:
                mensagem = res.get("message", "Nenhuma mensagem retornada.")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Não foi possível criar o lead: {mensagem}",
                )
            return schemas.LeadCreate(id=id_lead)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {e}",
            )

    @staticmethod
    async def cliente_existe(cpf_cnpj: str) -> schemas.ClienteExisteOut:
        try:
            # --- Busca de cliente no Opa ---
            cpf_cnpj_limpo = utils.Formatter.only_digits(cpf_cnpj)
            cliente_existe = await clients.OpaCliente.cliente_existe(
                cpf_cnpj_limpo=cpf_cnpj_limpo
            )
            return schemas.ClienteExisteOut(cliente_existe=cliente_existe)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {e}",
            )

    @staticmethod
    async def put_lead(cnpj_cpf: str, lead: schemas.LeadUpdate) -> schemas.LeadOut:
        try:
            # --- Lead ---
            endpoint = "contato"
            cnpj_cpf_formatado = utils.Formatter.cnpj_cpf(cnpj_cpf)
            grid_param = [
                {"TB": "contato.cnpj_cpf", "OP": "=", "P": cnpj_cpf_formatado}
            ]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, detail="Lead não encontrado."
                )
            lead_antigo = regs[0]

            # --- Lead atualizado ---
            lead_in_data = lead.model_dump(exclude_none=True)
            lead_atualizado: dict[str, Any] = {**lead_antigo, **lead_in_data}
            del lead_atualizado["id"]

            # --- Atualiza lead ---
            endpoint = "contato"
            id = lead_antigo["id"]
            payload = lead_atualizado
            await clients.IXCCliente.put(endpoint=endpoint, id=id, payload=payload)

            return schemas.LeadOut(**lead_atualizado)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {e}",
            )
