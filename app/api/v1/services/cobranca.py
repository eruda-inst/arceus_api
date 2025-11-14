from . import service
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Self, Optional
from .. import utils, schemas, clients
from fastapi import HTTPException, status
from pydantic import ValidationError, PositiveInt


class CobrancaService(service.Service):
    """
    Serviço para encapsular a lógica de negócios relacionada às operações de cobrança.
    """

    def __init__(self: Self) -> None:
        """
        Inicializa o serviço financeiro com o cliente IXC correspondente.
        """
        super().__init__()
        self.financeiro_ixc_cliente = clients.FinanceiroIXCCliente()

    async def get_faturas_vencidas(
        self: Self,
        protocolo: Optional[str] = None,
        cnpj_cpf: Optional[str] = None,
        page: Optional[PositiveInt] = 1,
        per_page: Optional[PositiveInt] = 15,
        sortname: Optional[str] = "fn_areceber.id",
        sortorder: Optional[utils.SortOrder] = utils.SortOrder.ASC,
    ) -> schemas.FaturaAbertaListOut:
        """
        Obtém uma lista paginada de faturas vencidas para um cliente.

        Args:
            protocolo: O protocolo de atendimento para identificar o cliente.
            cnpj_cpf: O CPF ou CNPJ do cliente.
            page: O número da página para a paginação.
            per_page: A quantidade de itens por página.
            sortname: O campo para ordenação.
            sortorder: A ordem de ordenação.

        Returns:
            Uma lista paginada e formatada de faturas vencidas.

        Raises:
            HTTPException: Se o cliente ou as faturas não forem encontrados, ou em caso de erro.
        """
        try:
            id_cliente = await self.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            res = await self.financeiro_ixc_cliente.get_faturas_abertas(
                id_cliente=id_cliente,
                page=page,
                per_page=per_page,
                sortname=sortname,
                sortorder=sortorder,
            )

            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Cliente sem faturas."
                )

            faturas_abertas_e_parciais = res["registros"]

            faturas_abertas_formatadas = []

            for fatura_aberta_e_parcial in faturas_abertas_e_parciais:
                data_hoje = (
                    datetime.now(ZoneInfo("America/Sao_Paulo")).date().isoformat()
                )

                data_vencimento = fatura_aberta_e_parcial["data_vencimento"]

                if fatura_aberta_e_parcial["status"] != "A":
                    continue

                if data_vencimento >= data_hoje:
                    continue

                id_contrato = fatura_aberta_e_parcial["id_contrato"]
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
                        "id": fatura_aberta_e_parcial["id"],
                        "id_contrato": fatura_aberta_e_parcial["id_contrato"],
                        "data_vencimento": data_vencimento,
                        "preco": fatura_aberta_e_parcial["valor"],
                        "contrato": contrato,
                    }
                )

            total = int(res.get("total", 0))

            meta = schemas.Meta(
                total=total,
                page=page,
                per_page=per_page,
            )

            return schemas.FaturaAbertaListOut(
                data=[schemas.FaturaAberta(**f) for f in faturas_abertas_formatadas],
                meta=meta,
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
