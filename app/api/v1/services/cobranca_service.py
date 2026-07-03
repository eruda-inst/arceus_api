from . import service_service
from datetime import datetime
from zoneinfo import ZoneInfo
from .. import schemas, clients
from pydantic import PositiveInt
from fastapi import HTTPException, status


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

            # --- Faturas abertas ---
            endpoint = "fn_areceber"
            grid_param = [
                {"TB": "fn_areceber.id_cliente", "OP": "=", "P": str(id_cliente)},
                {"TB": "fn_areceber.status", "OP": "!=", "P": "R"},
                {"TB": "fn_areceber.status", "OP": "!=", "P": "C"},
            ]
            res = await clients.IXCCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Faturas não encontradas.",
                )
            faturas_abertas = regs

            faturas_vencidas_parciais: list[schemas.FaturaAberta] = []

            # --- Data de hoje ---
            timezone = ZoneInfo("America/Bahia")
            datetime_hoje = datetime.now(tz=timezone)
            data_hoje = datetime_hoje.date()
            data_hoje_iso = data_hoje.isoformat()  # YYYY-MM-DD

            # --- Iteração entre faturas abertas ---
            for fatura_aberta in faturas_abertas:
                data_vencimento_iso = fatura_aberta["data_vencimento"]  # YYYY-MM-DD

                # Pula faturas não vencidas
                if data_hoje_iso <= data_vencimento_iso:
                    continue

                # --- Contrato ---
                endpoint = "cliente_contrato"
                id_contrato = fatura_aberta["id_contrato"]
                grid_param = [
                    {"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}
                ]
                res = await clients.IXCCliente.get(
                    endpoint=endpoint, grid_param=grid_param
                )
                regs = res.get("registros", [])
                if not regs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Contrato não encontrado.",
                    )
                contrato = regs[0]

                # --- Faturas vencidas parciais ---
                faturas_vencidas_parciais.append(
                    schemas.FaturaAberta(
                        id=fatura_aberta["id"],
                        id_contrato=fatura_aberta["id_contrato"],
                        contrato=contrato["contrato"],
                        data_vencimento=fatura_aberta["data_vencimento"],
                        preco=fatura_aberta["valor"],
                    )
                )

            return schemas.FaturaAbertaListOut(
                data=faturas_vencidas_parciais,
                meta=schemas.Meta(
                    total_itens=len(faturas_vencidas_parciais),
                    pagina_atual=pagina,
                    itens_por_pagina=itens_por_pagina,
                ),
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {e}",
            )
