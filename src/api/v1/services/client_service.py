import re
from typing import Any

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt

from .. import clients, services, utils


class ClientService:
    @staticmethod
    async def get_cliente_ixc(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_cliente: NonNegativeInt | None = None,
        protocolo: str | None = None,
        cnpj_cpf: str | None = None,
    ) -> dict[str, Any]:
        endpoint_cliente_ixc = "cliente"

        if id_cliente is not None:
            # --- Cliente IXC por id ---
            grid_param = [utils.Param(TB="cliente.id", P=id_cliente)]
            res = await clients.IxcClient.get(
                endpoint=endpoint_cliente_ixc, grid_param=grid_param
            )
            if not (regs := res.get("registros", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente inexistente no IXC",
                )
            cliente_ixc = regs[0]
            return cliente_ixc
        elif cnpj_cpf is not None and not re.match(pattern=r"{{\w+}}", string=cnpj_cpf):
            # --- Cliente IXC por cnpj_cpf ---
            cnpj_cpf_formatado = utils.Formatter.cnpj_cpf(cnpj_cpf=cnpj_cpf)
            grid_param = [utils.Param(TB="cliente.cnpj_cpf", P=cnpj_cpf_formatado)]
            res = await clients.IxcClient.get(
                endpoint=endpoint_cliente_ixc, grid_param=grid_param
            )
            if not (regs := res.get("registros", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente inexistente no IXC",
                )
            cliente_ixc = regs[0]
            return cliente_ixc
        elif protocolo is not None and not re.match(
            pattern=r"{{\w+}}", string=protocolo
        ):
            # --- Cliente Opa por protocolo ---
            endpoint = "atendimento"
            filter = {"protocolo": protocolo}
            res = await clients.OpaClient.get(endpoint=endpoint, filter=filter)
            if not (data := res.get("data", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente inexistente no Opa",
                )
            cliente_opa = data[0]

            # --- Cliente Opa por id ---
            endpoint = "cliente"
            filter = {"_id": cliente_opa["id_cliente"]}
            res = await clients.OpaClient.get(endpoint=endpoint, filter=filter)
            if not (data := res.get("data", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente inexistente no IXC",
                )
            cliente_opa = data[0]

            # --- Cliente IXC por id ---
            grid_param = [utils.Param(TB="cliente.id", P=cliente_opa["id"])]
            res = await clients.IxcClient.get(
                endpoint=endpoint_cliente_ixc, grid_param=grid_param
            )
            if not (regs := res.get("registros", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente inexistente no IXC",
                )
            cliente_ixc = regs[0]
            return cliente_ixc
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça id_cliente, cnpj_cpf ou protocolo",
            )

    @classmethod
    async def get_contratos(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_cliente: NonNegativeInt | None = None,
        protocolo: str | None = None,
        cnpj_cpf: str | None = None,
        pagina: PositiveInt | None = None,
        itens_por_pagina: PositiveInt | None = None,
    ) -> list[dict[str, Any]]:
        # --- Obtém cliente ---
        cliente = await cls.get_cliente_ixc(
            id_cliente=id_cliente, protocolo=protocolo, cnpj_cpf=cnpj_cpf
        )

        # --- Obtém contratos ---
        endpoint = "cliente_contrato"
        grid_param = [utils.Param(TB="cliente_contrato.id_cliente", P=cliente["id"])]
        res = await clients.IxcClient.get(
            endpoint=endpoint,
            grid_param=grid_param,
            pagina=pagina,
            itens_por_pagina=itens_por_pagina,
        )
        contratos = res.get("registros", [])

        contratos_parciais: list[dict[str, Any]] = []

        # Iteração entre contratos
        for contrato in contratos:
            id_contrato = contrato["id"]

            # --- Obtém login ---
            endpoint = "radusuarios"
            grid_param = [utils.Param(TB="radusuarios.id_contrato", P=id_contrato)]
            res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            login = regs[0] if len(regs) > 0 else {}

            # Nome do cliente
            nome = cliente.get("nome")
            razao = cliente.get("razao")
            nome_cliente = str(nome if nome else razao)

            # Fatura referência
            fatura_referencia: (
                dict[str, Any] | None
            ) = await services.FinanceiroService.get_fatura_referencia(
                id_contrato=id_contrato
            )

            # Dados fatura
            fatura_parcial = {"valor_fatura": None, "dia_vencimento_fatura": None}

            if fatura_referencia:
                fatura_parcial["valor_fatura"] = fatura_referencia["valor"]
                fatura_parcial["dia_vencimento_fatura"] = fatura_referencia[
                    "dia_vencimento_fatura"
                ]

            # Contrato parcial
            contratos_parciais.append(
                {
                    "id": id_contrato,
                    "id_login": login.get("id"),
                    "id_cliente": int(contrato["id_cliente"]),
                    "nome_cliente": nome_cliente,
                    "status": contrato["status"],
                    "status_acesso": contrato["status_internet"],
                    "nome_plano": contrato["contrato"],
                    "valor_fatura": fatura_parcial["valor_fatura"],
                    "dia_vencimento_fatura": fatura_parcial["dia_vencimento_fatura"],
                    "mac_onu": login.get("onu_mac"),
                    "id_plano": int(contrato["id_vd_contrato"]),
                }
            )

        return contratos_parciais

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
        res = await clients.IxcClient.get(
            endpoint=endpoint,
            grid_param=grid_param,
            pagina=pagina,
            itens_por_pagina=itens_por_pagina,
        )
        contratos = res.get("registros", [])

        contratos_parciais: list[dict[str, Any]] = []

        # --- Iteração entre contratos ---
        for contrato in contratos:
            id_contrato = contrato["id"]

            # --- Login ---
            endpoint = "radusuarios"
            grid_param = [utils.Param(TB="radusuarios.id_contrato", P=id_contrato)]
            res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
            if not (regs := res.get("registros", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Login inexistente"
                )
            login = regs[0]

            # --- Nome do cliente ---
            nome = cliente.get("nome")
            razao = cliente.get("razao")
            nome_cliente = str(nome if nome else razao)

            # --- Fatura referência ---
            fatura_referencia: (
                dict[str, Any] | None
            ) = await services.FinanceiroService.get_fatura_referencia(
                id_contrato=id_contrato
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
                    "id_login": int(login["id"]),
                    "id_cliente": int(contrato["id_cliente"]),
                    "nome_cliente": nome_cliente,
                    "status": contrato["status"],
                    "status_acesso": contrato["status_internet"],
                    "nome_plano": contrato["contrato"],
                    "valor_fatura": fatura_parcial["valor_fatura"],
                    "dia_vencimento_fatura": fatura_parcial["dia_vencimento_fatura"],
                    "mac_onu": login["onu_mac"] if login["onu_mac"] else None,
                    "id_plano": int(contrato["id_vd_contrato"]),
                }
            )

        return contratos_parciais
