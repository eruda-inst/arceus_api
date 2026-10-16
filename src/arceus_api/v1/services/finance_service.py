"""
Service for financial operations (invoices, Pix, credentials, unlock).
"""

import datetime as dt
import statistics
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt
from starlette.status import HTTP_404_NOT_FOUND

from .. import clients, config, schemas, services, utils


class FinanceService:
    """
    Provides static/class methods for financial operations.
    """

    @staticmethod
    async def _get_last_paid_invoice(
        # IDs NonNegativeInt, because IXC
        contract_id: NonNegativeInt,
    ) -> dict[str, Any] | None:
        """
        Retrieve the last paid invoice (as reference) for a contract.

        Uses the mode of the last 3 paid invoices to determine the most likely
        value and due day.

        Args:
            contract_id: Contract ID in IXC.

        Returns:
            A dict with invoice reference data, or None if no paid invoices exist.
        """
        # --- Get paid invoices ---
        endpoint = "fn_areceber"
        grid_param = [
            utils.Param(TB="fn_areceber.id_contrato", P=contract_id),
            utils.Param(TB="fn_areceber.status", P="R"),
        ]
        res = await clients.IxcClient.get(
            endpoint=endpoint,
            grid_param=grid_param,
            sort_order=utils.SortOrder.DESC,
        )
        if not (faturas_pagas := res.get("registros", [])):
            return None

        last_paid_invoices = faturas_pagas[:3]
        last_paid_invoice = last_paid_invoices[0]

        # Compute mode of values and due days from the last 3 invoices
        values = [float(u["valor"]) for u in last_paid_invoices]
        value = statistics.mode(values)

        due_dates = [u["data_vencimento"] for u in last_paid_invoices]
        due_days = [d.split("-")[2] for d in due_dates]
        due_day = statistics.mode(due_days)

        return {
            "id": int(last_paid_invoice["id"]),
            "status": last_paid_invoice["status"],
            "dia_vencimento_fatura": due_day,
            "valor": value,
        }

    @staticmethod
    async def _get_next_open_invoice(
        # IDs NonNegativeInt, because IXC
        contract_id: NonNegativeInt,
    ) -> dict[str, Any] | None:
        """
        Retrieve the next open invoice (as reference) for a contract.

        Uses the mode of the first 3 open invoices to determine the most likely
        value and due day.

        Args:
            contract_id: Contract ID in IXC.

        Returns:
            A dict with invoice reference data, or None if no open invoices exist.
        """
        # --- Get open invoices ---
        endpoint = "fn_areceber"
        grid_param = [
            utils.Param(TB="fn_areceber.id_contrato", P=contract_id),
            utils.Param(TB="fn_areceber.status", OP="!=", P="R"),
            utils.Param(TB="fn_areceber.status", OP="!=", P="C"),
        ]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (faturas_abertas := res.get("registros", [])):
            return None

        next_open_invoices = faturas_abertas[:3]
        next_open_invoice = next_open_invoices[0]

        values = [float(p["valor"]) for p in next_open_invoices]
        value = statistics.mode(values)

        due_dates = [p["data_vencimento"] for p in next_open_invoices]
        due_days = [d.split("-")[2] for d in due_dates]
        due_day = statistics.mode(due_days)

        return {
            "id": int(next_open_invoice["id"]),
            "status": next_open_invoice["status"],
            "dia_vencimento_fatura": due_day,
            "valor": value,
        }

    @classmethod
    async def get_invoice_reference(
        cls,
        # IDs NonNegativeInt, because IXC
        contract_id: NonNegativeInt,
    ) -> dict[str, Any] | None:
        """
        Get an invoice reference for a contract.

        Prefers the next open invoice, falling back to the last paid invoice.

        Args:
            contract_id: Contract ID in IXC.

        Returns:
            The reference invoice dict, or None if no invoices exist.
        """
        next_open_invoice = await cls._get_next_open_invoice(contract_id=contract_id)

        if next_open_invoice:
            return next_open_invoice

        last_paid_invoice = await cls._get_last_paid_invoice(contract_id=contract_id)

        return last_paid_invoice

    @staticmethod
    async def get_open_invoices(
        # IDs NonNegativeInt, because IXC
        contract_id: NonNegativeInt,
        page: PositiveInt,
        items_per_page: PositiveInt,
    ) -> schemas.ListOutSchema[schemas.InvoiceOutSchema]:
        """
        Retrieve all open invoices for a contract.

        Args:
            contract_id: Contract ID in IXC.
            page: Page number for pagination.
            items_per_page: Items per page.

        Returns:
            A paginated list of InvoiceOutSchema.

        Raises:
            HTTPException: 404 if the contract does not exist.
        """
        # --- Get contract ---
        endpoint = "cliente_contrato"
        grid_param = [utils.Param(TB="cliente_contrato.id", P=contract_id)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Contrato inexistente"
            )
        contract = regs[0]

        # --- Get open invoices ---
        endpoint = "fn_areceber"
        grid_param = [
            utils.Param(TB="fn_areceber.id_contrato", P=contract_id),
            utils.Param(TB="fn_areceber.status", OP="!=", P="R"),
            utils.Param(TB="fn_areceber.status", OP="!=", P="C"),
        ]
        res = await clients.IxcClient.get(
            endpoint=endpoint,
            grid_param=grid_param,
            pagina=page,
            itens_por_pagina=items_per_page,
        )
        open_invoices = res.get("registros", [])

        partial_open_invoices: list[schemas.InvoiceOutSchema] = []

        for open_invoice in open_invoices:
            partial_open_invoices.append(
                schemas.InvoiceOutSchema(
                    id=open_invoice["id"],
                    contrato=contract["contrato"],
                    data_vencimento=open_invoice["data_vencimento"],
                    id_contrato=contract_id,
                    preco=open_invoice["valor"],
                )
            )

        return schemas.ListOutSchema[schemas.InvoiceOutSchema](
            data=partial_open_invoices,
            meta=schemas.MetaOutSchema(
                total_itens=len(partial_open_invoices),
                pagina_atual=page,
                itens_por_pagina=items_per_page,
            ),
        )

    @staticmethod
    async def get_3_open_invoices(
        # IDs NonNegativeInt, because IXC
        contract_id: NonNegativeInt,
        page: PositiveInt,
        items_per_page: PositiveInt,
    ) -> schemas.ListOutSchema[schemas.InvoiceOutSchema]:
        """
        Retrieve a smart selection of up to 3 open invoices for a contract.

        The selection depends on how many overdue invoices exist:
        - 0 overdue: return the first 3 open invoices.
        - 1 overdue: return up to 3 invoices.
        - >1 overdue: return invoices up to (and including) the current month.

        Args:
            contract_id: Contract ID in IXC.
            page: Page number for pagination.
            items_per_page: Items per page.

        Returns:
            A ListOutSchema with the selected InvoiceOutSchema items.

        Raises:
            HTTPException: 404 if the contract does not exist.
        """
        # --- Get contract ---
        endpoint = "cliente_contrato"
        grid_param = [utils.Param(TB="cliente_contrato.id", P=contract_id)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Contrato inexistente"
            )
        contract = regs[0]

        # --- Get open invoices ---
        endpoint = "fn_areceber"
        grid_param = [
            utils.Param(TB="fn_areceber.id_contrato", P=contract_id),
            utils.Param(TB="fn_areceber.status", OP="!=", P="R"),
            utils.Param(TB="fn_areceber.status", OP="!=", P="C"),
        ]
        res = await clients.IxcClient.get(
            endpoint=endpoint,
            grid_param=grid_param,
            pagina=page,
            itens_por_pagina=items_per_page,
        )
        open_invoices = res.get("registros", [])

        partial_open_invoices: list[schemas.InvoiceOutSchema] = []

        total_overdue_invoices = 0
        now = dt.datetime.now(ZoneInfo(config.settings.timezone))
        actual_date = now.date()
        actual_iso_date = actual_date.isoformat()  # AAAA-MM-DD
        actual_month = str(actual_date.month).zfill(2)  # 01, instead of 1, for example

        # Count overdue invoices (excluding the current month)
        for open_invoice in open_invoices:
            due_date = dt.date.fromisoformat(open_invoice["data_vencimento"])
            due_month = str(due_date.month).zfill(2)
            if actual_month == due_month:
                continue
            if actual_iso_date > open_invoice["data_vencimento"]:
                total_overdue_invoices += 1

        if total_overdue_invoices == 0:
            open_invoices = open_invoices[:3]
            for open_invoice in open_invoices:
                partial_open_invoices.append(
                    schemas.InvoiceOutSchema(
                        id=open_invoice["id"],
                        contrato=contract["contrato"],
                        data_vencimento=open_invoice["data_vencimento"],
                        id_contrato=contract_id,
                        preco=open_invoice["valor"],
                    )
                )
        elif total_overdue_invoices == 1:
            for open_invoice in open_invoices:
                partial_open_invoices.append(
                    schemas.InvoiceOutSchema(
                        id=open_invoice["id"],
                        contrato=contract["contrato"],
                        data_vencimento=open_invoice["data_vencimento"],
                        id_contrato=contract_id,
                        preco=open_invoice["valor"],
                    )
                )
                if len(partial_open_invoices) == 3:
                    break
        else:
            for open_invoice in open_invoices:
                partial_open_invoices.append(
                    schemas.InvoiceOutSchema(
                        id=open_invoice["id"],
                        contrato=contract["contrato"],
                        data_vencimento=open_invoice["data_vencimento"],
                        id_contrato=contract_id,
                        preco=open_invoice["valor"],
                    )
                )
                due_date = dt.date.fromisoformat(open_invoice["data_vencimento"])
                due_month = str(due_date.month).zfill(2)
                # Stop once we reach the current month's invoice
                if actual_month == due_month:
                    break

        return schemas.ListOutSchema[schemas.InvoiceOutSchema](
            data=partial_open_invoices,
            meta=schemas.MetaOutSchema(
                total_itens=len(partial_open_invoices),
                pagina_atual=page,
                itens_por_pagina=items_per_page,
            ),
        )

    @staticmethod
    async def post_trusted_unlock(
        # IDs NonNegativeInt, because IXC
        contract_id: NonNegativeInt,
    ) -> schemas.MessageOutSchema:
        """
        Perform a trusted unlock for a contract in IXC.

        Args:
            contract_id: Contract ID in IXC.

        Returns:
            A MessageOutSchema indicating success.

        Raises:
            HTTPException: 500 if the unlock fails.
        """
        # --- Post trusted unlock ---
        endpoint = "desbloqueio_confianca"
        payload = {"id": contract_id}
        res = await clients.IxcClient.post(endpoint=endpoint, payload=payload)
        if res["type"] == "error":
            msg = res.get("message", "Desbloqueio malsucedido")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=utils.Formatter.sanitize(string=msg),
            )

        return schemas.MessageOutSchema(mensagem="Desbloqueio bem-sucedido")

    @staticmethod
    async def get_digitable_line(
        # IDs NonNegativeInt, because IXC
        invoice_id: NonNegativeInt,
    ) -> schemas.DigitableLineOutSchema:
        """
        Retrieve the digitable line (barcode) for an invoice.

        Args:
            invoice_id: Invoice ID in IXC.

        Returns:
            DigitableLineOutSchema containing the digitable line.

        Raises:
            HTTPException: 404 if the invoice or digitable line does not exist.
        """
        # --- Get invoice ---
        endpoint = "fn_areceber"
        grid_param = [utils.Param(TB="fn_areceber.id", P=invoice_id)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Fatura inexistente"
            )
        invoice = regs[0]

        if not (digitable_line := invoice.get("linha_digitavel")):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Linha digitável inexistente",
            )

        return schemas.DigitableLineOutSchema(linha_digitavel=digitable_line)

    @staticmethod
    async def get_pix_key(
        # IDs NonNegativeInt, because IXC
        invoice_id: NonNegativeInt,
    ) -> schemas.PixKeyOutSchema:
        """
        Retrieve the Pix key for an invoice from SevenAZ.

        Args:
            invoice_id: Invoice ID.

        Returns:
            PixKeyOutSchema containing the Pix key.

        Raises:
            HTTPException: 404 if the invoice or Pix key does not exist.
        """
        # --- Get invoice ---
        endpoint = f"invoices/{invoice_id}/payment-data"
        res = await clients.SevenAZClient.get(endpoint=endpoint)

        if "id" not in res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Fatura inexistente"
            )

        if not (pix_key := res.get("pixCode")):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chave pix inexistente",
            )

        return schemas.PixKeyOutSchema(chave_pix=pix_key)

    @staticmethod
    async def get_credentials(
        # IDs NonNegativeInt, because IXC
        customer_id: NonNegativeInt,
    ) -> schemas.CredentialOutSchema:
        """
        Retrieve subscriber central credentials for a customer.

        Args:
            customer_id: Customer ID in IXC.

        Returns:
            CredentialOutSchema with username and password.
        """
        # --- Get customer ---
        customer = await services.CustomerService.get_ixc_customer(
            customer_id=customer_id
        )

        return schemas.CredentialOutSchema(
            usuario=customer["hotsite_email"], senha=customer["senha"]
        )

    @staticmethod
    async def patch_credentials(
        # IDs NonNegativeInt, because IXC
        customer_id: NonNegativeInt,
        password: str,
    ) -> schemas.CredentialOutSchema:
        """
        Update subscriber central password for a customer.

        Args:
            customer_id: Customer ID in IXC.
            password: New plaintext password.

        Returns:
            CredentialOutSchema with the updated credentials.

        Raises:
            HTTPException: 500 if the update fails.
        """
        # --- Get customer ---
        old_customer = await services.CustomerService.get_ixc_customer(
            customer_id=customer_id
        )

        updated_customer: dict[str, Any] = {**old_customer, "senha": password}
        del updated_customer["id"]

        # --- Put customer ---
        id = old_customer["id"]
        endpoint = f"cliente/{id}"
        res = await clients.IxcClient.put(endpoint=endpoint, payload=updated_customer)
        if res["type"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cadastro malsucedido",
            )

        return schemas.CredentialOutSchema(
            usuario=updated_customer["hotsite_email"], senha=password
        )
