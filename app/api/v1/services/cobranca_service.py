from . import ClienteService
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import PositiveInt
from .. import schemas, clients, utils
from fastapi import HTTPException, status


class CobrancaService:
    @staticmethod
    async def get_faturas_vencidas(
        protocolo: str | None,
        cnpj_cpf: str | None,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.FaturaListOut:
        try:
            if not protocolo and not cnpj_cpf:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Informe protocolo ou cnpj_cpf.",
                )

            # --- Obtém cliente ---
            cliente = await ClienteService.get_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            # --- Obtém faturas abertas ---
            endpoint = "fn_areceber"
            grid_param = [
                utils.Param(TB="fn_areceber.id_cliente", P=cliente["id"]),
                utils.Param(TB="fn_areceber.status", OP="!=", P="R"),
                utils.Param(TB="fn_areceber.status", OP="!=", P="C"),
            ]
            res = await clients.IxcCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )
            regs = res.get("registros", [])
            faturas_abertas = regs

            faturas_vencidas_parciais: list[schemas.FaturaOut] = []

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
                res = await clients.IxcCliente.get(
                    endpoint=endpoint, grid_param=grid_param
                )
                regs = res.get("registros", [])
                if not regs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Contrato inexistente.",
                    )
                contrato = regs[0]

                # Faturas vencidas parciais
                faturas_vencidas_parciais.append(
                    schemas.FaturaOut(
                        id=fatura_aberta["id"],
                        id_contrato=fatura_aberta["id_contrato"],
                        contrato=contrato["contrato"],
                        data_vencimento=fatura_aberta["data_vencimento"],
                        preco=fatura_aberta["valor"],
                    )
                )

            return schemas.FaturaListOut(
                data=faturas_vencidas_parciais,
                meta=schemas.Meta(
                    total_itens=len(faturas_vencidas_parciais),
                    pagina_atual=pagina,
                    itens_por_pagina=itens_por_pagina,
                ),
            )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )
