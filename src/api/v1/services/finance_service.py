import statistics
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt
from starlette.status import HTTP_404_NOT_FOUND

from .. import clients, schemas, services, utils
from . import CustomerService


class FinanceService:
    @staticmethod
    async def _get_last_paid_invoice(
        # IDs NonNegativeInt, pois o IXC é quebrado
        contract_id: NonNegativeInt,
    ) -> dict[str, Any] | None:
        # --- Obtém faturas pagas ---
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

        # Ultima fatura paga
        last_paid_invoices = faturas_pagas[:3]
        last_paid_invoice = last_paid_invoices[0]

        # Valor da fatura
        values = [float(u["valor"]) for u in last_paid_invoices]
        value = statistics.mode(values)

        # Dia de vencimento da fatura
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
        # IDs NonNegativeInt, pois o IXC é quebrado
        contract_id: NonNegativeInt,
    ) -> dict[str, Any] | None:
        # --- Obtém faturas abertas ---
        endpoint = "fn_areceber"
        grid_param = [
            utils.Param(TB="fn_areceber.id_contrato", P=contract_id),
            utils.Param(TB="fn_areceber.status", OP="!=", P="R"),
            utils.Param(TB="fn_areceber.status", OP="!=", P="C"),
        ]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (faturas_abertas := res.get("registros", [])):
            return None

        # Proxima fatura aberta
        next_open_invoices = faturas_abertas[:3]
        next_open_invoice = next_open_invoices[0]

        # Valor da fatura
        values = [float(p["valor"]) for p in next_open_invoices]
        value = statistics.mode(values)

        # Dia de vencimento da fatura
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
        # IDs NonNegativeInt, pois o IXC é quebrado
        contract_id: NonNegativeInt,
    ) -> dict[str, Any] | None:
        next_open_invoice = await cls._get_next_open_invoice(contract_id=contract_id)

        if next_open_invoice:
            return next_open_invoice

        last_paid_invoice = await cls._get_last_paid_invoice(contract_id=contract_id)

        return last_paid_invoice

    @staticmethod
    async def get_open_invoices(
        # IDs NonNegativeInt, pois o IXC é quebrado
        contract_id: NonNegativeInt,
        page: PositiveInt,
        items_per_page: PositiveInt,
    ) -> schemas.ListOutSchema[schemas.InvoiceOutSchema]:
        # --- Obtém contrato ---
        endpoint = "cliente_contrato"
        grid_param = [utils.Param(TB="cliente_contrato.id", P=contract_id)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Contrato inexistente"
            )
        contract = regs[0]

        # --- Obtém faturas Abertas ---
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

        # Iteração entre faturas abertas
        for open_invoice in open_invoices:
            # Faturas abertas parciais
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
        # IDs NonNegativeInt, pois o IXC é quebrado
        contract_id: NonNegativeInt,
        page: PositiveInt,
        items_per_page: PositiveInt,
    ) -> schemas.ListOutSchema[schemas.InvoiceOutSchema]:
        # --- Obtém contrato ---
        endpoint = "cliente_contrato"
        grid_param = [utils.Param(TB="cliente_contrato.id", P=contract_id)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Contrato inexistente"
            )
        contract = regs[0]

        # --- Obtém faturas Abertas ---
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
        now = datetime.now(ZoneInfo("America/Bahia"))
        actual_date = now.date()
        actual_iso_date = actual_date.isoformat()  # AAAA-MM-DD
        actual_month = str(actual_date.month).zfill(2)  # 01, ao invés de 1, por exemplo

        for open_invoice in open_invoices:
            due_date = date.fromisoformat(open_invoice["data_vencimento"])
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
                due_date = date.fromisoformat(open_invoice["data_vencimento"])
                due_month = str(due_date.month).zfill(2)
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
        # IDs NonNegativeInt, pois o IXC é quebrado
        contract_id: NonNegativeInt,
    ) -> schemas.MessageOutSchema:
        # --- Realiza desbloqueio de confiança ---
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
        # IDs NonNegativeInt, pois o IXC é quebrado
        invoice_id: NonNegativeInt,
    ) -> schemas.DigitableLineOutSchema:
        # --- Obtém fatura ---
        endpoint = "fn_areceber"
        grid_param = [utils.Param(TB="fn_areceber.id", P=invoice_id)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Fatura inexistente"
            )
        invoice = regs[0]

        # Linha digitável
        if not (digitable_line := invoice.get("linha_digitavel")):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Linha digitável inexistente",
            )

        return schemas.DigitableLineOutSchema(linha_digitavel=digitable_line)

    @staticmethod
    async def get_pix_key(
        # IDs NonNegativeInt, pois o IXC é quebrado
        invoice_id: NonNegativeInt,
    ) -> schemas.PixKeyOutSchema:
        # --- Obtém fatura ---
        endpoint = f"invoices/{invoice_id}/payment-data"
        res = await clients.SevenAZClient.get(endpoint=endpoint)

        if "id" not in res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Fatura inexistente"
            )

        # Chave pix
        if not (pix_key := res.get("pixCode")):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chave pix inexistente",
            )

        return schemas.PixKeyOutSchema(chave_pix=pix_key)

    @staticmethod
    async def get_credentials(
        # IDs NonNegativeInt, pois o IXC é quebrado
        customer_id: NonNegativeInt,
    ) -> schemas.CredentialOutSchema:
        # --- Obtém cliente ---
        customer = await CustomerService.get_ixc_customer(customer_id=customer_id)

        return schemas.CredentialOutSchema(
            usuario=customer["hotsite_email"], senha=customer["senha"]
        )

    @staticmethod
    async def patch_credentials(
        # IDs NonNegativeInt, pois o IXC é quebrado
        customer_id: NonNegativeInt,
        password: str,
    ) -> schemas.CredentialOutSchema:
        # --- Obtém cliente atual ---
        old_customer = await services.CustomerService.get_ixc_customer(
            customer_id=customer_id
        )

        # Cliente atualizado
        updated_customer: dict[str, Any] = {**old_customer, "senha": password}
        del updated_customer["id"]

        # --- Atualiza cliente ---
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
