from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt

from .. import clients, schemas, utils


class CobrancaService:
    @staticmethod
    async def get_faturas_vencidas(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_contrato: NonNegativeInt,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.ListOutSchema[schemas.FaturaOutSchema]:
        # --- Obtém contrato ---
        endpoint = "cliente_contrato"
        grid_param = [utils.Param(TB="cliente_contrato.id", P=id_contrato)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contrato inexistente"
            )
        contrato = regs[0]

        # --- Obtém faturas Abertas ---
        endpoint = "fn_areceber"
        grid_param = [
            utils.Param(TB="fn_areceber.id_contrato", P=id_contrato),
            utils.Param(TB="fn_areceber.status", OP="!=", P="R"),
            utils.Param(TB="fn_areceber.status", OP="!=", P="C"),
        ]
        res = await clients.IxcClient.get(
            endpoint=endpoint,
            grid_param=grid_param,
            pagina=pagina,
            itens_por_pagina=itens_por_pagina,
        )
        faturas_abertas = res.get("registros", [])

        faturas_vencidas_parciais: list[schemas.FaturaOutSchema] = []

        # Data de hoje
        timezone = ZoneInfo("America/Bahia")
        datetime_hoje = datetime.now(tz=timezone)
        data_hoje = datetime_hoje.date()
        data_hoje_iso = data_hoje.isoformat()  # YYYY-MM-DD

        # Iteração entre faturas abertas
        for fatura_aberta in faturas_abertas:
            data_vencimento_iso = fatura_aberta["data_vencimento"]  # YYYY-MM-DD

            # Pula faturas não vencidas
            # Datas em formato ISO podem ser comparadas como comparações convencionais entre strings
            if data_hoje_iso <= data_vencimento_iso:
                continue

            # --- Obtém contrato ---
            endpoint = "cliente_contrato"
            id_contrato = fatura_aberta["id_contrato"]
            grid_param = [utils.Param(TB="cliente_contrato.id", P=id_contrato)]
            res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
            if not (regs := res.get("registros", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Contrato inexistente",
                )
            contrato = regs[0]

            # Faturas vencidas parciais
            faturas_vencidas_parciais.append(
                schemas.FaturaOutSchema(
                    id=fatura_aberta["id"],
                    id_contrato=fatura_aberta["id_contrato"],
                    contrato=contrato["contrato"],
                    data_vencimento=fatura_aberta["data_vencimento"],
                    preco=fatura_aberta["valor"],
                )
            )

        return schemas.ListOutSchema[schemas.FaturaOutSchema](
            data=faturas_vencidas_parciais,
            meta=schemas.MetaOutSchema(
                total_itens=len(faturas_vencidas_parciais),
                pagina_atual=pagina or 1,
                itens_por_pagina=itens_por_pagina or 10,
            ),
        )
