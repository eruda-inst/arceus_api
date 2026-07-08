from typing import Any
from . import ClienteService
from fastapi import HTTPException, status
from pydantic import PositiveInt, NonNegativeInt
from .. import utils, schemas, clients, services


class ComercialService:
    @staticmethod
    async def get_status_acesso(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_contrato: NonNegativeInt,
    ) -> schemas.StatusInternetOut:
        try:
            # --- Contrato ---
            endpoint = "cliente_contrato"
            grid_param = [
                {"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}
            ]
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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def get_contratos(
        protocolo: str | None,
        cnpj_cpf: str | None,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.ComercialContratoListOut:
        try:
            # --- Cliente ---
            cliente = await ClienteService.get_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            # --- Contratos ---
            endpoint = "cliente_contrato"
            grid_param = [
                {
                    "TB": "cliente_contrato.id_cliente",
                    "OP": "=",
                    "P": str(cliente["id"]),
                },
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "I"},
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "N"},
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "D"},
            ]
            res = await clients.IxcCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )
            regs = res.get("registros", [])
            total = res.get("total", 0)
            contratos = regs

            contratos_parciais: list[schemas.ComercialContratoOut] = []

            # --- Iteração entre contratos ---
            for contrato in contratos:
                id_contrato = contrato.get("id")

                # --- Login ---
                endpoint = "radusuarios"
                grid_param = [
                    {"TB": "radusuarios.id_contrato", "OP": "=", "P": str(id_contrato)}
                ]
                res = await clients.IxcCliente.get(
                    endpoint=endpoint, grid_param=grid_param
                )
                regs = res.get("registros", [])
                if not regs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Login inexistente.",
                    )
                login = regs[0]

                # --- Fatura referência ---
                fatura_referencia: dict[str, Any] | None = (
                    await services.FinanceiroService.get_fatura_referencia(
                        id_contrato=id_contrato
                    )
                )
                if not fatura_referencia:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Fatura referência inexistente.",
                    )

                # --- Nome do cliente ---
                nome = cliente.get("nome")
                razao = cliente.get("razao")
                nome_cliente = nome if nome else razao

                # --- Contrato parcial ---
                contratos_parciais.append(
                    schemas.ComercialContratoOut(
                        id=id_contrato,
                        contrato=contrato["contrato"],
                        nome_cliente=nome_cliente,
                        valor=fatura_referencia["valor"],
                        status_acesso=contrato["status_internet"],
                        data_vencimento=fatura_referencia["data_vencimento"],
                        id_cliente=cliente["id"],
                        id_login=login["id"],
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
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def post_leads(lead: schemas.LeadIn) -> schemas.LeadOut:
        try:
            # --- Lead ---
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

            # --- Lead criado ---
            grid_param = [{"TB": "contato.id", "OP": "=", "P": str(id)}]
            res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            lead_criado = regs[0]

            return schemas.LeadOut(
                id=lead_criado["id"],
                ativo=lead_criado["ativo"],
                bairro=lead_criado["bairro"],
                cep=lead_criado["cep"],
                cidade=lead_criado["cidade"],
                cnpj_cpf=lead_criado["cnpj_cpf"],
                data_nascimento=lead_criado["data_nascimento"],
                email=lead_criado["email"],
                endereco=lead_criado["endereco"],
                fone_celular=lead_criado["fone_celular"],
                fone_whatsapp=lead_criado["fone_whatsapp"],
                id_candidato_tipo=lead_criado["id_candidato_tipo"],
                id_filial=lead_criado["id_filial"],
                id_responsavel=lead_criado["id_responsavel"],
                id_vd_contrato=lead_criado["id_vd_contrato"],
                lead=lead_criado["lead"],
                nome=lead_criado["nome"],
                numero=lead_criado["numero"],
                obs=lead_criado["obs"],
                principal=lead_criado["principal"],
                tipo_pessoa=lead_criado["tipo_pessoa"],
                uf=lead_criado["uf"],
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def cliente_existe(cpf_cnpj: str) -> schemas.ClienteExisteOut:
        try:
            # --- Busca de cliente no Opa ---
            cpf_cnpj_limpo = utils.Formatter.only_digits(cpf_cnpj)
            endpoint = "cliente"
            filter = {"cpf_cnpj": cpf_cnpj_limpo}
            options = {"limit": 1}
            res = await clients.OpaCliente.get(
                endpoint=endpoint, filter=filter, options=options
            )
            cliente_existe = True
            data = res.get("data")
            if not data:
                cliente_existe = False

            return schemas.ClienteExisteOut(cliente_existe=cliente_existe)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
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
            res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, detail="Lead inexistente."
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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )
