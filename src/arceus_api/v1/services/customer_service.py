"""
Service for customer-related operations.

Provides methods to look up customers in IXC and OPA systems.
"""

import re
from typing import Any

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt

from .. import clients, services, utils


class CustomerService:
    """
    Provides static/class methods for customer retrieval.
    """

    @staticmethod
    async def get_ixc_customer(
        # IDs NonNegativeInt, because IXC
        customer_id: NonNegativeInt | None = None,
        protocol: str | None = None,
        cnpj_cpf: str | None = None,
    ) -> dict[str, Any]:
        """
        Retrieve an IXC customer by ID, CNPJ/CPF, or OPA protocol.

        Args:
            customer_id: Customer ID in IXC.
            protocol: OPA service protocol.
            cnpj_cpf: Customer document (CNPJ or CPF).

        Returns:
            The IXC customer record as a dictionary.

        Raises:
            HTTPException: 400 if no valid search parameter is provided.
            HTTPException: 404 if the customer is not found.
        """
        ixc_customer_endpoint = "cliente"

        if customer_id is not None:
            # --- IXC customer by ID ---
            grid_param = [utils.Param(TB="cliente.id", P=customer_id)]
            res = await clients.IxcClient.get(
                endpoint=ixc_customer_endpoint, grid_param=grid_param
            )
            if not (regs := res.get("registros", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente inexistente no IXC",
                )
            ixc_customer = regs[0]
            return ixc_customer
        elif cnpj_cpf is not None and not re.match(pattern=r"{{\w+}}", string=cnpj_cpf):
            # --- IXC customer by cnpj_cpf ---
            formatted_cnpj_cpf = utils.Formatter.cnpj_cpf(cnpj_cpf=cnpj_cpf)
            grid_param = [utils.Param(TB="cliente.cnpj_cpf", P=formatted_cnpj_cpf)]
            res = await clients.IxcClient.get(
                endpoint=ixc_customer_endpoint, grid_param=grid_param
            )
            if not (regs := res.get("registros", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente inexistente no IXC",
                )
            ixc_customer = regs[0]
            return ixc_customer
        elif protocol is not None and not re.match(pattern=r"{{\w+}}", string=protocol):
            # --- Opa client by protocol ---
            endpoint = "atendimento"
            filter = {"protocolo": protocol}
            res = await clients.OpaClient.get(endpoint=endpoint, filter=filter)
            if not (data := res.get("data", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente inexistente no Opa",
                )
            opa_customer = data[0]

            # --- Opa customer by ID ---
            endpoint = "cliente"
            filter = {"_id": opa_customer["id_cliente"]}
            res = await clients.OpaClient.get(endpoint=endpoint, filter=filter)
            if not (data := res.get("data", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente inexistente no IXC",
                )
            opa_customer = data[0]

            # --- IXC customer by ID ---
            grid_param = [utils.Param(TB="cliente.id", P=opa_customer["id"])]
            res = await clients.IxcClient.get(
                endpoint=ixc_customer_endpoint, grid_param=grid_param
            )
            if not (regs := res.get("registros", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente inexistente no IXC",
                )
            ixc_customer = regs[0]
            return ixc_customer
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça id_cliente, cnpj_cpf ou protocolo",
            )

    @classmethod
    async def get_contracts(
        cls,
        # IDs NonNegativeInt, because IXC
        customer_id: NonNegativeInt | None = None,
        protocol: str | None = None,
        cnpj_cpf: str | None = None,
        page: PositiveInt | None = None,
        items_per_page: PositiveInt | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve contracts (with extra details) for a customer.

        Args:
            customer_id: Customer ID in IXC.
            protocol: OPA service protocol.
            cnpj_cpf: Customer document (CNPJ or CPF).
            page: Page number for pagination.
            items_per_page: Items per page.

        Returns:
            A list of dictionaries with enriched contract information.
        """
        # --- Get customer ---
        customer = await cls.get_ixc_customer(
            customer_id=customer_id, protocol=protocol, cnpj_cpf=cnpj_cpf
        )

        # --- Get contracts ---
        endpoint = "cliente_contrato"
        grid_param = [utils.Param(TB="cliente_contrato.id_cliente", P=customer["id"])]
        res = await clients.IxcClient.get(
            endpoint=endpoint,
            grid_param=grid_param,
            pagina=page,
            itens_por_pagina=items_per_page,
        )
        contracts = res.get("registros", [])

        partial_contracts: list[dict[str, Any]] = []

        for contract in contracts:
            contract_id = contract["id"]

            # --- Get login ---
            endpoint = "radusuarios"
            grid_param = [utils.Param(TB="radusuarios.id_contrato", P=contract_id)]
            res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            login = regs[0] if len(regs) > 0 else {}

            nome = customer.get("nome")
            razao = customer.get("razao")
            customer_name = str(nome if nome else razao)

            # --- Get invoice reference ---
            invoice_reference: (
                dict[str, Any] | None
            ) = await services.FinanceService.get_invoice_reference(
                contract_id=contract_id
            )

            partial_invoice = {"valor_fatura": None, "dia_vencimento_fatura": None}

            if invoice_reference:
                partial_invoice["valor_fatura"] = invoice_reference["valor"]
                partial_invoice["dia_vencimento_fatura"] = invoice_reference[
                    "dia_vencimento_fatura"
                ]

            partial_contracts.append(
                {
                    "id": contract_id,
                    "id_login": login.get("id"),
                    "id_cliente": int(contract["id_cliente"]),
                    "nome_cliente": customer_name,
                    "status": contract["status"],
                    "status_acesso": contract["status_internet"],
                    "nome_plano": contract["contrato"],
                    "valor_fatura": partial_invoice["valor_fatura"],
                    "dia_vencimento_fatura": partial_invoice["dia_vencimento_fatura"],
                    "mac_onu": login.get("onu_mac"),
                    "id_plano": int(contract["id_vd_contrato"]),
                }
            )

        return partial_contracts

    @classmethod
    async def get_active_contracts(
        cls,
        # IDs NonNegativeInt, because IXC
        customer_id: NonNegativeInt | None = None,
        protocol: str | None = None,
        cnpj_cpf: str | None = None,
        page: PositiveInt | None = None,
        items_per_page: PositiveInt | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve active contracts (non-inactive, non-negative, non-withdrawn) for a customer.

        Args:
            customer_id: Customer ID in IXC.
            protocol: OPA service protocol.
            cnpj_cpf: Customer document (CNPJ or CPF).
            page: Page number for pagination.
            items_per_page: Items per page.

        Returns:
            A list of dictionaries with enriched active contract information.

        Raises:
            HTTPException: 404 if a login is missing for a contract.
        """
        # --- Get customer ---
        customer = await cls.get_ixc_customer(
            customer_id=customer_id, protocol=protocol, cnpj_cpf=cnpj_cpf
        )

        # --- Get contracts ---
        endpoint = "cliente_contrato"
        grid_param = [
            utils.Param(TB="cliente_contrato.id_cliente", P=customer["id"]),
            utils.Param(TB="cliente_contrato.status", OP="!=", P="I"),
            utils.Param(TB="cliente_contrato.status", OP="!=", P="N"),
            utils.Param(TB="cliente_contrato.status", OP="!=", P="D"),
        ]
        res = await clients.IxcClient.get(
            endpoint=endpoint,
            grid_param=grid_param,
            pagina=page,
            itens_por_pagina=items_per_page,
        )
        contracts = res.get("registros", [])

        partial_contracts: list[dict[str, Any]] = []

        for contract in contracts:
            contract_id = contract["id"]

            # --- Get login ---
            endpoint = "radusuarios"
            grid_param = [utils.Param(TB="radusuarios.id_contrato", P=contract_id)]
            res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
            if not (regs := res.get("registros", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Login inexistente"
                )
            login = regs[0]

            nome = customer.get("nome")
            razao = customer.get("razao")
            customer_name = str(nome if nome else razao)

            # --- Get invoice reference ---
            invoice_reference: (
                dict[str, Any] | None
            ) = await services.FinanceService.get_invoice_reference(
                contract_id=contract_id
            )

            partial_invoice = {"valor_fatura": None, "dia_vencimento_fatura": None}

            if invoice_reference:
                partial_invoice["valor_fatura"] = invoice_reference["valor"]
                partial_invoice["dia_vencimento_fatura"] = invoice_reference[
                    "dia_vencimento_fatura"
                ]

            partial_contracts.append(
                {
                    "id": contract_id,
                    "id_login": int(login["id"]),
                    "id_cliente": int(contract["id_cliente"]),
                    "nome_cliente": customer_name,
                    "status": contract["status"],
                    "status_acesso": contract["status_internet"],
                    "nome_plano": contract["contrato"],
                    "valor_fatura": partial_invoice["valor_fatura"],
                    "dia_vencimento_fatura": partial_invoice["dia_vencimento_fatura"],
                    "mac_onu": login["onu_mac"] if login["onu_mac"] else None,
                    "id_plano": int(contract["id_vd_contrato"]),
                }
            )

        return partial_contracts
