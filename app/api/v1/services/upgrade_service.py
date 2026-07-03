from .. import clients, schemas
from pydantic import PositiveInt
from fastapi import HTTPException, status


class UpgradeService:
    @staticmethod
    async def get_planos_sugeridos(
        id_cliente: PositiveInt,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.PlanoSugeridoListOut:
        try:
            grid_param = [
                {"TB": "cliente_contrato.id_cliente", "OP": "=", "P": str(id_cliente)},
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "I"},
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "N"},
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "D"},
            ]
            endpoint = "cliente_contrato"
            contratos_res = await clients.IXCCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )

            contratos = contratos_res.get("registros", [])

            ids_planos_basicos = [277, 278, 279, 280, 281]
            ids_planos_gamers = [267, 272]
            ids_planos_oficiais = ids_planos_basicos.copy()
            ids_planos_oficiais.extend(ids_planos_gamers)

            ids_str = (str(id) for id in ids_planos_basicos)
            ids_str_tratados = str(",").join(ids_str)
            grid_param = [{"TB": "vd_contratos.id", "OP": "IN", "P": ids_str_tratados}]
            planos_oficiais_res = await clients.IXCCliente.get(
                endpoint="vd_contratos",
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )
            planos_oficiais = planos_oficiais_res.get("registros", [])

            planos_oficiais = sorted(
                planos_oficiais, key=lambda p: float(p["valor_contrato"])
            )
            for plano_oficial in planos_oficiais:
                plano_oficial["valor_contrato"] = float(plano_oficial["valor_contrato"])

            planos_sugeridos: list[schemas.PlanoSugeridoOut] = []

            for contrato in contratos:
                id_vd_contrato = int(contrato.get("id_vd_contrato", None))

                if id_vd_contrato in ids_planos_oficiais:
                    continue

                grid_param = [
                    {"TB": "vd_contratos.id", "OP": "=", "P": str(id_vd_contrato)}
                ]
                plano_vigente_res = await clients.IXCCliente.get(
                    endpoint="vd_contratos",
                    grid_param=grid_param,
                    pagina=pagina,
                    itens_por_pagina=itens_por_pagina,
                )
                plano_vigente = plano_vigente_res.get("registros", [])
                plano_atual = {}
                plano_atual["nome"] = plano_vigente[0].get("nome", None)
                plano_atual["valor"] = float(
                    plano_vigente[0].get("valor_contrato", None)
                )

                plano_sugerido = {}

                if plano_atual["valor"] < planos_oficiais[0]["valor_contrato"]:
                    plano_sugerido["nome"] = planos_oficiais[0]["nome"]
                    plano_sugerido["valor"] = planos_oficiais[0]["valor_contrato"]
                elif plano_atual["valor"] < planos_oficiais[1]["valor_contrato"]:
                    plano_sugerido["nome"] = planos_oficiais[1]["nome"]
                    plano_sugerido["valor"] = planos_oficiais[1]["valor_contrato"]
                elif plano_atual["valor"] < planos_oficiais[2]["valor_contrato"]:
                    plano_sugerido["nome"] = planos_oficiais[2]["nome"]
                    plano_sugerido["valor"] = planos_oficiais[2]["valor_contrato"]
                elif plano_atual["valor"] < planos_oficiais[3]["valor_contrato"]:
                    plano_sugerido["nome"] = planos_oficiais[3]["nome"]
                    plano_sugerido["valor"] = planos_oficiais[3]["valor_contrato"]
                else:
                    plano_sugerido["nome"] = planos_oficiais[4]["nome"]
                    plano_sugerido["valor"] = planos_oficiais[4]["valor_contrato"]

                planos_sugeridos.append(
                    schemas.PlanoSugeridoOut(
                        nome_plano_atual=plano_atual["nome"],
                        valor_plano_atual=plano_atual["valor"],
                        nome_plano_sugerido=plano_sugerido["nome"],
                        valor_plano_sugerido=plano_sugerido["valor"],
                    )
                )

            meta = schemas.Meta(
                total_itens=len(planos_sugeridos),
                pagina_atual=pagina,
                itens_por_pagina=itens_por_pagina,
            )

            return schemas.PlanoSugeridoListOut(data=planos_sugeridos, meta=meta)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {e}",
            )
