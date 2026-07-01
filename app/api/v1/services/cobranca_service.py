from typing import List, Any
from . import service_service
from datetime import datetime
from zoneinfo import ZoneInfo
from .. import schemas, clients
from fastapi import HTTPException, status
from pydantic import ValidationError, PositiveInt


class CobrancaService(service_service.Service):
    @classmethod
    async def get_faturas_vencidas(
        cls,
        protocolo: str | None,
        cnpj_cpf: str | None,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.FaturaAbertaListOut:
        try:
            id_cliente = await cls.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            grid_param = [
                {"TB": "fn_areceber.id_cliente", "OP": "=", "P": str(id_cliente)},
                {"TB": "fn_areceber.status", "OP": "=", "P": "A"},
            ]

            res = await clients.IXCCliente.get(
                endpoint="fn_areceber",
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )

            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Cliente sem faturas."
                )

            faturas_abertas_e_parciais = res["registros"]

            faturas_abertas_formatadas: List[Any] = []

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
                endpoint = "cliente_contrato"
                grid_param = [
                    {"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}
                ]
                contrato_res = await clients.IXCCliente.get(
                    endpoint=endpoint, grid_param=grid_param
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
                total_itens=total,
                pagina_atual=pagina,
                itens_por_pagina=itens_por_pagina,
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
