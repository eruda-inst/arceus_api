from typing import Any

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt

from .. import clients, schemas, services, utils


class UpgradeService:
    _ids_planos_em_uso = (277, 278, 279, 280, 281)

    @classmethod
    async def _get_planos_em_uso(cls) -> list[dict[str, Any]]:
        # --- Obtém planos em uso ---
        ids_str = (str(id) for id in cls._ids_planos_em_uso)
        ids_str_tratados = ",".join(ids_str)
        endpoint = "vd_contratos"
        grid_param = [utils.Param(TB="vd_contratos.id", OP="IN", P=ids_str_tratados)]
        res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
        planos_em_uso = res.get("registros", [])

        planos_em_uso_parciais: list[dict[str, Any]] = []

        for p in planos_em_uso:
            planos_em_uso_parciais.append(
                {
                    "id": p["id"],
                    "nome": p["nome"],
                    "valor": float(p["valor_contrato"]),
                }
            )

        # Ordena planos em ordem crescente por valor
        planos_em_uso_parciais = sorted(
            planos_em_uso_parciais, key=lambda p: p["valor"]
        )

        return planos_em_uso_parciais

    @classmethod
    async def get_planos_sugeridos(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_cliente: NonNegativeInt,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.ListOut[schemas.PlanoSugeridoOut]:
        # --- Obtém contratos ativos ---
        contratos = await services.ClienteService.get_contratos_ativos(
            id_cliente=id_cliente, pagina=pagina, itens_por_pagina=itens_por_pagina
        )

        # IDs de planos
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

        # --- Obtém planos para checar ---
        planos_para_checar = await cls._get_planos_em_uso()

        planos_sugeridos: list[schemas.PlanoSugeridoOut] = []

        # Iteração entre contratos
        for contrato in contratos:
            id_plano = contrato["id_plano"]

            # Se o plano do cliente estiver na lista de planos para ignorar
            if id_plano in ids_planos_para_ignorar:
                continue

            # --- Obtém plano atual do cliente ---
            endpoint = "vd_contratos"
            grid_param = [utils.Param(TB="vd_contratos.id", P=id_plano)]
            res = await clients.IxcCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )
            if not (regs := res.get("registros", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Plano inexistente",
                )
            plano_cliente = regs[0]
            # Converte valor do plano do cliente para float
            plano_cliente: dict[str, Any] = {
                **plano_cliente,
                "valor_contrato": float(plano_cliente["valor_contrato"]),
            }

            # --- Obtém fatura referência ---
            fatura_referencia = await services.FinanceiroService.get_fatura_referencia(
                id_contrato=contrato["id"]
            )

            # O valor que o cliente realmente paga vem de fatura_referencia
            if fatura_referencia:
                plano_cliente = {
                    **plano_cliente,
                    "valor_contrato": fatura_referencia["valor"],
                }

            # Se o plano do cliente estiver na lista de planos para checar
            if plano_cliente["id"] in cls._ids_planos_em_uso:
                # Plano referência, i.e., mesmo plano do cliente, mas com valor sem descontos/acréscimos
                planos_referencia: list[dict[str, Any]] = [
                    p for p in planos_para_checar if p["id"] == plano_cliente["id"]
                ]
                plano_referencia = planos_referencia[0]
                valor_plano_referencia = float(plano_referencia["valor_contrato"])

                # Se o cliente paga mais do que deveria
                if plano_cliente["valor_contrato"] > valor_plano_referencia:
                    # Iteração entre planos para checar
                    for p in planos_para_checar:
                        # Se o valor do plano sugerido for maior que o do plano do cliente
                        if p["valor"] > plano_cliente["valor_contrato"]:
                            planos_sugeridos.append(
                                schemas.PlanoSugeridoOut(
                                    nome_plano_atual=plano_cliente["nome"],
                                    valor_plano_atual=plano_cliente["valor_contrato"],
                                    nome_plano_sugerido=p["nome"],
                                    valor_plano_sugerido=p["valor"],
                                )
                            )
                            break
            # Se o plano do cliente não estiver na lista de planos para checar
            else:
                melhor_plano = planos_para_checar[-1]

                # Se o cliente pagar igual ou mais que o melhor plano
                if plano_cliente["valor_contrato"] >= melhor_plano["valor"]:
                    planos_sugeridos.append(
                        schemas.PlanoSugeridoOut(
                            nome_plano_atual=plano_cliente["nome"],
                            valor_plano_atual=plano_cliente["valor_contrato"],
                            nome_plano_sugerido=melhor_plano["nome"],
                            valor_plano_sugerido=melhor_plano["valor"],
                        )
                    )
                    continue

                # Iteração entre planos para checar
                for p in planos_para_checar:
                    # Se o valor do plano para checar for maior ou igual ao do plano do cliente
                    if p["valor"] >= plano_cliente["valor_contrato"]:
                        planos_sugeridos.append(
                            schemas.PlanoSugeridoOut(
                                nome_plano_atual=plano_cliente["nome"],
                                valor_plano_atual=plano_cliente["valor_contrato"],
                                nome_plano_sugerido=p["nome"],
                                valor_plano_sugerido=p["valor"],
                            )
                        )
                        break

        return schemas.ListOut[schemas.PlanoSugeridoOut](
            data=planos_sugeridos,
            meta=schemas.MetaOut(
                total_itens=len(planos_sugeridos),
                pagina_atual=pagina or 1,
                itens_por_pagina=itens_por_pagina or 10,
            ),
        )
