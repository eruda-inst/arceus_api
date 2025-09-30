from .. import schemas
from .service import Service
from ..utils import SortOrder
from typing import Self, Optional
from fastapi import HTTPException, status
from ..clients import FinanceiroIXCCliente
from pydantic import ValidationError, PositiveInt


class FinanceiroService(Service):
    def __init__(self: Self) -> None:
        super().__init__()
        self.financeiro_ixc_cliente = FinanceiroIXCCliente()

    async def get_faturas_abertas(
        self: Self,
        protocolo: str,
        page: Optional[PositiveInt] = 1,
        per_page: Optional[PositiveInt] = 10,
        sortname: Optional[str] = "fn_areceber.id",
        sortorder: Optional[SortOrder] = SortOrder.ASC,
    ) -> schemas.FaturaAbertaListOut:
        try:
            id_cliente = await self.get_id_cliente_ixc(protocolo=protocolo)

            faturas_abertas = await self.financeiro_ixc_cliente.get_faturas_abertas(
                id_cliente=id_cliente,
                page=page,
                per_page=per_page,
                sortname=sortname,
                sortorder=sortorder,
            )

            if not faturas_abertas.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Cliente sem faturas."
                )

            faturas_abertas = faturas_abertas["registros"]

            faturas_abertas_formatadas = []

            for fatura_aberta in faturas_abertas:
                id_contrato = fatura_aberta["id_contrato"]
                contrato_res = await self.financeiro_ixc_cliente.get_contrato(
                    id_contrato=id_contrato
                )
                contrato = (
                    contrato_res["registros"][0]["contrato"]
                    if contrato_res.get("registros")
                    else "N/A"
                )
                faturas_abertas_formatadas.append(
                    {
                        "id": fatura_aberta["id"],
                        "id_contrato": fatura_aberta["id_contrato"],
                        "data_vencimento": fatura_aberta["data_vencimento"],
                        "preco": fatura_aberta["valor"],
                        "contrato": contrato,
                    }
                )

            total = len(faturas_abertas)

            meta = schemas.Meta(
                total=total,
                page=page,
                per_page=per_page,
            )

            base_url = f"/api/v1/financeiro/faturas?protocolo={protocolo}"
            links = schemas.Links(
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

            return schemas.FaturaAbertaListOut(
                data=[schemas.FaturaAberta(**f) for f in faturas_abertas_formatadas],
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

    async def post_desbloqueio_em_confianca(
        self: Self, id_contrato: PositiveInt
    ) -> schemas.MensagemOut:
        try:
            res = await self.financeiro_ixc_cliente.post_desbloqueio_em_confianca(
                id_contrato=id_contrato
            )
            mensagem = res.get("message")
            return schemas.MensagemOut(mensagem=mensagem)
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

    async def get_linha_digitavel(
        self: Self, id: PositiveInt
    ) -> schemas.LinhaDigitavelOut:
        try:
            res = await self.financeiro_ixc_cliente.get_linha_digitavel(id=id)
            reg = res.get("registros")
            if not reg:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sem linha digitável.",
                )
            linha_digitavel = reg[0]["linha_digitavel"]
            return schemas.LinhaDigitavelOut(
                data=schemas.LinhaDigitavelBase(linha_digitavel=linha_digitavel)
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
