from typing import Any
from .. import clients, schemas, utils, services
from fastapi import HTTPException, status
from pydantic import PositiveInt, NonNegativeInt


class UpgradeService:
    @staticmethod
    async def get_planos_sugeridos(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_cliente: NonNegativeInt,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.PlanoSugeridoListOut:
        try:
            # --- Obtém contratos ativos ---
            contratos = await services.ClienteService.get_contratos_ativos(
                id_cliente=id_cliente
            )

            # IDs de planos
            ids_planos_padrao = (277, 278, 279, 280, 281)
            ids_planos_para_ignorar = (
                267,
                272,
                266,
                249,
                247,
                224,
                217,
                215,
                211,
                203,
                172,
                166,
                162,
                127,
                126,
                244,
            )

            # --- Obtém planos padrão ---
            ids_str = (str(id) for id in ids_planos_padrao)
            ids_str_tratados = str(",").join(ids_str)
            endpoint = "vd_contratos"
            grid_param = [
                utils.Param(TB="vd_contratos.id", OP="IN", P=ids_str_tratados)
            ]
            res = await clients.IxcCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )
            regs = res.get("registros", [])
            planos_padrao = regs

            # Ordenação de planos, para facilitar a lógica
            planos_padrao = sorted(
                planos_padrao, key=lambda p: float(p["valor_contrato"])
            )

            # Conversão de valores para float, para realização de cálculos aritméticos
            for plano_padrao in planos_padrao:
                plano_padrao["valor_contrato"] = float(plano_padrao["valor_contrato"])

            planos_sugeridos: list[schemas.PlanoSugeridoOut] = []

            # Iteração entre contratos
            for contrato in contratos:
                id_vd_contrato = contrato["id_plano"]

                # Caso I: Se o plano atual estiver na lista de planos para ignorar
                if id_vd_contrato in ids_planos_para_ignorar:
                    continue

                # --- Obtém plano atual do cliente ---
                endpoint = "vd_contratos"
                grid_param = [
                    utils.Param(TB="vd_contratos.id", OP="=", P=id_vd_contrato)
                ]
                res = await clients.IxcCliente.get(
                    endpoint=endpoint,
                    grid_param=grid_param,
                    pagina=pagina,
                    itens_por_pagina=itens_por_pagina,
                )
                regs = res.get("registros", [])
                plano_cliente: dict[str, Any] = regs[0]
                plano_cliente = {
                    **plano_cliente,
                    "valor_contrato": float(plano_cliente["valor_contrato"]),
                }

                # --- Obtém fatura referência ---
                fatura_referencia = (
                    await services.FinanceiroService.get_fatura_referencia(
                        id_contrato=contrato["id"]
                    )
                )

                if fatura_referencia:
                    plano_cliente = {
                        **plano_cliente,
                        "valor_contrato": fatura_referencia["valor"],
                    }

                # Caso II: Se o plano atual estiver na lista de planos padrão
                if plano_cliente["id"] in [p_p["id"] for p_p in planos_padrao]:
                    # Se o valor do plano atual for maior que o valor do plano referência
                    plano_referencia: dict[str, Any] = [
                        p_p for p_p in planos_padrao if p_p["id"] == id_vd_contrato
                    ][0]
                    plano_referencia: dict[str, Any] = {
                        **plano_referencia,
                        "valor_contrato": float(plano_referencia["valor_contrato"]),
                    }
                    if (
                        plano_cliente["valor_contrato"]
                        > plano_referencia["valor_contrato"]
                    ):
                        for plano_padrao in planos_padrao:
                            if (
                                plano_padrao["valor_contrato"]
                                > plano_cliente["valor_contrato"]
                            ):
                                valor_acrescimo = plano_padrao["valor_contrato"] - (
                                    plano_cliente["valor_contrato"]
                                )
                                planos_sugeridos.append(
                                    schemas.PlanoSugeridoOut(
                                        nome_plano_atual=plano_cliente["nome"],
                                        valor_plano_atual=plano_cliente[
                                            "valor_contrato"
                                        ],
                                        nome_plano_sugerido=plano_padrao["nome"],
                                        valor_plano_sugerido=plano_padrao[
                                            "valor_contrato"
                                        ],
                                        valor_acrescimo=valor_acrescimo,
                                    )
                                )
                                break
                # Caso III: Se o plano atual não estiver na lista de planos padrão
                else:
                    for plano_padrao in planos_padrao:
                        if (
                            plano_padrao["valor_contrato"]
                            >= plano_cliente["valor_contrato"]
                        ):
                            valor_acrescimo = plano_padrao["valor_contrato"] - (
                                plano_cliente["valor_contrato"]
                            )
                            planos_sugeridos.append(
                                schemas.PlanoSugeridoOut(
                                    nome_plano_atual=plano_cliente["nome"],
                                    valor_plano_atual=plano_cliente["valor_contrato"],
                                    nome_plano_sugerido=plano_padrao["nome"],
                                    valor_plano_sugerido=plano_padrao["valor_contrato"],
                                    valor_acrescimo=valor_acrescimo,
                                )
                            )
                            break

            return schemas.PlanoSugeridoListOut(
                data=planos_sugeridos,
                meta=schemas.Meta(
                    total_itens=len(planos_sugeridos),
                    pagina_atual=pagina,
                    itens_por_pagina=itens_por_pagina,
                ),
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )
