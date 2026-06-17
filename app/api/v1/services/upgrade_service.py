from pydantic import PositiveInt
from .. import clients, schemas, utils
from fastapi import HTTPException, status


class UpgradeService:
    @staticmethod
    async def get_planos_sugeridos(
        id_cliente: PositiveInt,
        page: int | None = 1,
        per_page: int | None = 10,
        sortname: str | None = "cliente_contrato.id",
        sortorder: utils.SortOrder | None = utils.SortOrder.ASC,
    ) -> schemas.PlanoSugeridoListOut:
        try:
            contratos_res = await clients.SuporteIXCCliente.get_contratos(
                id_cliente=id_cliente,
                page=page,
                per_page=per_page,
                sortname=sortname,
                sortorder=sortorder,
            )
            contratos = contratos_res.get("registros", [])

            ids_planos_oficiais = [277, 278, 279, 280, 281]
            planos_oficiais_res = await clients.UpgradeIXCCliente.get_planos(
                ids=ids_planos_oficiais
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

                plano_vigente_res = await clients.UpgradeIXCCliente.get_plano(
                    id_vd_contrato=id_vd_contrato
                )
                plano_vigente = plano_vigente_res.get("registros", [])
                plano_atual = {}
                plano_atual["nome"] = plano_vigente.get("nome", None)
                plano_atual["valor"] = float(plano_vigente.get("valor_contrato", None))

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
                total=len(planos_sugeridos), page=page, per_page=per_page
            )

            return schemas.PlanoSugeridoListOut(data=planos_sugeridos, meta=meta)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )
