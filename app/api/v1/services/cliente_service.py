from typing import Any
from pydantic import PositiveInt, NonNegativeInt
from .. import clients, utils, services
from fastapi import HTTPException, status


class ClienteService:

    @staticmethod
    async def get_cliente_ixc(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_cliente: NonNegativeInt | None = None,
        protocolo: str | None = None,
        cnpj_cpf: str | None = None,
    ) -> dict[str, Any]:
        endpoint_cliente_ixc = "cliente"

        try:
            if id_cliente:
                # --- Cliente IXC por ID ---
                grid_param = [utils.Param(TB="cliente.cnpj_cpf", P=id_cliente)]
                res = await clients.IxcCliente.get(
                    endpoint=endpoint_cliente_ixc, grid_param=grid_param
                )
                regs = res.get("registros", [])
                if not regs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cliente inexistente no IXC.",
                    )
                cliente_ixc = regs[0]
                return cliente_ixc
            if cnpj_cpf:
                # --- Cliente IXC por cnpj_cpf ---
                cnpj_cpf_formatado = utils.Formatter.cnpj_cpf(cnpj_cpf=cnpj_cpf)
                grid_param = [utils.Param(TB="cliente.cnpj_cpf", P=cnpj_cpf_formatado)]
                res = await clients.IxcCliente.get(
                    endpoint=endpoint_cliente_ixc, grid_param=grid_param
                )
                regs = res.get("registros", [])
                if not regs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cliente inexistente no IXC.",
                    )
                cliente_ixc = regs[0]
                return cliente_ixc
            elif protocolo:
                # --- Cliente Opa por protocolo ---
                endpoint = "atendimento"
                filter = {"protocolo": protocolo}
                res = await clients.OpaCliente.get(endpoint=endpoint, filter=filter)
                data = res.get("data", [])
                if not data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cliente inexistente no Opa.",
                    )
                cliente_opa = data[0]

                # --- Cliente Opa por ID ---
                endpoint = "cliente"
                filter = {"_id": cliente_opa["id_cliente"]}
                res = await clients.OpaCliente.get(endpoint=endpoint, filter=filter)
                data = res.get("data", [])
                if not data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cliente inexistente no IXC.",
                    )
                cliente_opa = data[0]

                # --- Cliente IXC por ID ---
                grid_param = [utils.Param(TB="cliente.id", P=cliente_opa["id"])]
                res = await clients.IxcCliente.get(
                    endpoint=endpoint_cliente_ixc, grid_param=grid_param
                )
                regs = res.get("registros", [])
                if not regs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cliente inexistente no IXC.",
                    )
                cliente_ixc = regs[0]
                return cliente_ixc
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Forneça cnpj_cpf ou protocolo.",
                )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )

    @classmethod
    async def get_contratos_ativos(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_cliente: NonNegativeInt | None = None,
        protocolo: str | None = None,
        cnpj_cpf: str | None = None,
        pagina: PositiveInt | None = None,
        itens_por_pagina: PositiveInt | None = None,
    ) -> list[dict[str, Any]]:
        try:
            # --- Cliente ---
            cliente = await cls.get_cliente_ixc(
                id_cliente=id_cliente, protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            # --- Contratos ---
            endpoint = "cliente_contrato"
            grid_param = [
                utils.Param(TB="cliente_contrato.id_cliente", P=cliente["id"]),
                utils.Param(TB="cliente_contrato.status", OP="!=", P="I"),
                utils.Param(TB="cliente_contrato.status", OP="!=", P="N"),
                utils.Param(TB="cliente_contrato.status", OP="!=", P="D"),
            ]
            res = await clients.IxcCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )
            regs = res.get("registros", [])
            contratos = regs

            contratos_parciais: list[dict[str, Any]] = []

            # --- Iteração entre contratos ---
            for contrato in contratos:
                id_contrato = contrato.get("id")

                # --- Login ---
                endpoint = "radusuarios"
                grid_param = [utils.Param(TB="radusuarios.id_contrato", P=id_contrato)]
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

                # --- Nome do cliente ---
                nome = cliente.get("nome")
                razao = cliente.get("razao")
                nome_cliente = str(nome if nome else razao)

                # --- Fatura referência ---
                fatura_referencia: dict[str, Any] | None = (
                    await services.FinanceiroService.get_fatura_referencia(
                        id_contrato=id_contrato
                    )
                )

                # --- Dados fatura ---
                fatura_parcial = {"valor_fatura": None, "dia_vencimento_fatura": None}

                if fatura_referencia:
                    fatura_parcial["valor_fatura"] = fatura_referencia["valor"]
                    fatura_parcial["dia_vencimento_fatura"] = fatura_referencia[
                        "dia_vencimento_fatura"
                    ]

                # --- Contrato parcial ---
                contratos_parciais.append(
                    {
                        "id": id_contrato,
                        "id_login": login["id"],
                        "id_cliente": contrato["id_cliente"],
                        "nome_cliente": nome_cliente,
                        "status": contrato["status"],
                        "status_acesso": contrato["status_internet"],
                        "nome_plano": contrato["contrato"],
                        "valor_fatura": fatura_parcial["valor_fatura"],
                        "dia_vencimento_fatura": fatura_parcial[
                            "dia_vencimento_fatura"
                        ],
                        "mac_onu": login["onu_mac"] if login["onu_mac"] else None,
                    }
                )

            return contratos_parciais
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )
