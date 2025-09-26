from ..utils import SortOrder
from typing import Self, Optional
from pydantic import ValidationError, PositiveInt
from fastapi import HTTPException, status
from ..clients import FinanceiroIXCCliente, FinanceiroOpaCliente
from ..schemas import Fatura, FaturaOut, Meta, Links


class FinanceiroService:
    def __init__(self: Self) -> None:
        self.ixc_cliente = FinanceiroIXCCliente()
        self.opa_cliente = FinanceiroOpaCliente()

    async def get_faturas(
        self: Self,
        protocolo: str,
        page: Optional[PositiveInt] = 1,
        per_page: Optional[PositiveInt] = 10,
        sortname: Optional[str] = "fn_areceber.id",
        sortorder: Optional[SortOrder] = SortOrder.ASC,
    ) -> FaturaOut:
        try:
            id_cliente_opa_res = await self.opa_cliente.get_id_cliente_opa(
                protocolo=protocolo
            )
            if not id_cliente_opa_res.get("data", []):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado no OPA.",
                )
            id_cliente_opa = id_cliente_opa_res["data"][0]["id_cliente"]

            id_cliente_ixc_res = await self.opa_cliente.get_id_cliente_ixc(
                id_cliente_opa=id_cliente_opa
            )
            if not id_cliente_ixc_res.get("data", []):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado no IXC.",
                )
            id_cliente_ixc = id_cliente_ixc_res["data"][0]["id"]

            faturas_res = await self.ixc_cliente.get_faturas(
                id_cliente=id_cliente_ixc,
                page=page,
                per_page=per_page,
                sortname=sortname,
                sortorder=sortorder,
            )

            if not faturas_res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Cliente sem faturas."
                )

            faturas = faturas_res["registros"]

            faturas_formatadas = []

            for fatura in faturas:
                id_contrato = fatura["id_contrato"]
                contrato_res = await self.ixc_cliente.get_contrato(
                    id_contrato=id_contrato
                )
                contrato = (
                    contrato_res["registros"][0]["contrato"]
                    if contrato_res.get("registros")
                    else "N/A"
                )
                faturas_formatadas.append(
                    {
                        "id": fatura["id"],
                        "id_contrato": fatura["id_contrato"],
                        "data_vencimento": fatura["data_vencimento"],
                        "preco": fatura["valor"],
                        "contrato": contrato,
                    }
                )

            total = len(faturas)

            meta = Meta(
                total=total,
                page=page,
                per_page=per_page,
            )

            base_url = f"/api/v1/financeiro/faturas?protocolo={protocolo}"
            links = Links(
                self=f"{base_url}&page={page}&per_page={per_page}",
                next=(
                    f"{base_url}&page={page + 1}&per_page={per_page}"
                    if (page * per_page) < total
                    else None
                ),
                prev=(
                    f"{base_url}&page={page - 1}&per_page={per_page}"
                    if page > 1
                    else None
                ),
            )

            return FaturaOut(
                data=[Fatura(**f) for f in faturas_formatadas],
                meta=meta,
                links=links,
            )
        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Validação da resposta falhou: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )
