"""
Service for billing-related operations (overdue invoices).
"""

import datetime as dt
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt

from .. import clients, schemas, utils


class BillingService:
    """
    Provides static methods for billing operations.
    """

    @staticmethod
    async def get_overdue_invoices(
        # IDs NonNegativeInt, because IXC
        contract_id: NonNegativeInt,
        page: PositiveInt,
        items_per_page: PositiveInt,
    ) -> schemas.ListOutSchema[schemas.InvoiceOutSchema]:
        """
        Retrieve overdue invoices for a given contract.

        Overdue means the invoice's due date is before today's date.

        Args:
            contract_id: Contract ID in IXC.
            page: Page number for pagination.
            items_per_page: Items per page.

        Returns:
            A ListOutSchema of InvoiceOutSchema containing only overdue invoices.

        Raises:
            HTTPException: 404 if the contract does not exist.
        """
        # --- Get contract ---
        endpoint = "cliente_contrato"
        grid_param = [utils.Param(TB="cliente_contrato.id", P=contract_id)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contrato inexistente"
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

        partial_overdue_invoices: list[schemas.InvoiceOutSchema] = []

        timezone = ZoneInfo("America/Bahia")
        now = dt.datetime.now(tz=timezone)
        today_date = now.date()
        iso_today_date = today_date.isoformat()  # YYYY-MM-DD

        for open_invoice in open_invoices:
            data_vencimento_iso = open_invoice["data_vencimento"]  # YYYY-MM-DD

            # Skip invoices that are not yet overdue
            if iso_today_date <= data_vencimento_iso:
                continue

            # --- Get contract ---
            endpoint = "cliente_contrato"
            id_contrato = open_invoice["id_contrato"]
            grid_param = [utils.Param(TB="cliente_contrato.id", P=id_contrato)]
            res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
            if not (regs := res.get("registros", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Contrato inexistente",
                )
            contract = regs[0]

            partial_overdue_invoices.append(
                schemas.InvoiceOutSchema(
                    id=open_invoice["id"],
                    id_contrato=open_invoice["id_contrato"],
                    contrato=contract["contrato"],
                    data_vencimento=open_invoice["data_vencimento"],
                    preco=open_invoice["valor"],
                )
            )

        return schemas.ListOutSchema[schemas.InvoiceOutSchema](
            data=partial_overdue_invoices,
            meta=schemas.MetaOutSchema(
                total_itens=len(partial_overdue_invoices),
                pagina_atual=page,
                itens_por_pagina=items_per_page,
            ),
        )
