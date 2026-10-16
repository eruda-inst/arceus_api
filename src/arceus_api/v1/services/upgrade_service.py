"""
Service for upgrade operations (suggested plans).
"""

from typing import Any

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt

from .. import clients, schemas, services, utils


class UpgradeService:
    """
    Provides class methods for suggesting plan upgrades.
    """

    # IDs of the plans currently "in usage" for comparison purposes
    _plans_in_usage_id = (277, 278, 279, 280, 281)

    @classmethod
    async def _get_plans_in_usage(cls) -> list[dict[str, Any]]:
        """
        Retrieve the list of "in usage" plans from IXC, sorted by price.

        Returns:
            A list of dicts with id, name, and value for each plan.
        """
        # --- Get plans ---
        str_ids = (str(id) for id in cls._plans_in_usage_id)
        treated_str_ids = ",".join(str_ids)
        endpoint = "vd_contratos"
        grid_param = [utils.Param(TB="vd_contratos.id", OP="IN", P=treated_str_ids)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        plans_in_usage = res.get("registros", [])

        partial_plans_in_usage: list[dict[str, Any]] = []

        for plan_in_usage in plans_in_usage:
            partial_plans_in_usage.append(
                {
                    "id": plan_in_usage["id"],
                    "nome": plan_in_usage["nome"],
                    "valor": float(plan_in_usage["valor_contrato"]),
                }
            )

        # Sort plans by value for consistent comparisons
        partial_plans_in_usage = sorted(
            partial_plans_in_usage, key=lambda p: p["valor"]
        )

        return partial_plans_in_usage

    @classmethod
    async def get_suggested_plans(
        cls,
        # IDs NonNegativeInt, because IXC
        customer_id: NonNegativeInt,
        page: PositiveInt,
        items_per_page: PositiveInt,
    ) -> schemas.ListOutSchema[schemas.SuggestedPlanOutSchema]:
        """
        Suggest official plans to replace outdated customer plans.

        Args:
            customer_id: Customer ID in IXC.
            page: Page number.
            items_per_page: Items per page.

        Returns:
            A ListOutSchema of SuggestedPlanOutSchema.

        Raises:
            HTTPException: 404 if a plan is not found.
        """
        # --- Get contracts ---
        contracts = await services.CustomerService.get_active_contracts(
            customer_id=customer_id, page=page, items_per_page=items_per_page
        )

        # Plans to skip when suggesting upgrades
        plans_id_to_ignore = (
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

        # --- Get plans ---
        plans_to_check = await cls._get_plans_in_usage()

        suggested_plans: list[schemas.SuggestedPlanOutSchema] = []

        for contract in contracts:
            plan_id = contract["id_plano"]

            if plan_id in plans_id_to_ignore:
                continue

            # --- Get plan ---
            endpoint = "vd_contratos"
            grid_param = [utils.Param(TB="vd_contratos.id", P=plan_id)]
            res = await clients.IxcClient.get(
                endpoint=endpoint,
                grid_param=grid_param,
                pagina=page,
                itens_por_pagina=items_per_page,
            )
            if not (regs := res.get("registros", [])):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Plano inexistente",
                )
            customer_plan = regs[0]
            customer_plan: dict[str, Any] = {
                **customer_plan,
                "valor_contrato": float(customer_plan["valor_contrato"]),
            }

            # --- Get invoice reference ---
            invoice_reference = await services.FinanceService.get_invoice_reference(
                contract_id=contract["id"]
            )

            if invoice_reference:
                customer_plan = {
                    **customer_plan,
                    "valor_contrato": invoice_reference["valor"],
                }

            if int(customer_plan["id"]) in cls._plans_in_usage_id:
                # Customer is on an "in usage" plan: suggest a more expensive one
                plans_reference: list[dict[str, Any]] = [
                    p for p in plans_to_check if p["id"] == customer_plan["id"]
                ]
                plan_reference = plans_reference[0]
                plan_reference_value = float(plan_reference["valor"])

                if customer_plan["valor_contrato"] > plan_reference_value:
                    for plan_to_check in plans_to_check:
                        if plan_to_check["valor"] > customer_plan["valor_contrato"]:
                            suggested_plans.append(
                                schemas.SuggestedPlanOutSchema(
                                    nome_plano_atual=customer_plan["nome"],
                                    valor_plano_atual=customer_plan["valor_contrato"],
                                    nome_plano_sugerido=plan_to_check["nome"],
                                    valor_plano_sugerido=plan_to_check["valor"],
                                )
                            )
                            break
            else:
                # Customer is on an arbitrary plan: find closest plan
                best_plan = plans_to_check[-1]

                if customer_plan["valor_contrato"] >= best_plan["valor"]:
                    suggested_plans.append(
                        schemas.SuggestedPlanOutSchema(
                            nome_plano_atual=customer_plan["nome"],
                            valor_plano_atual=customer_plan["valor_contrato"],
                            nome_plano_sugerido=best_plan["nome"],
                            valor_plano_sugerido=best_plan["valor"],
                        )
                    )
                    continue

                for plan_to_check in plans_to_check:
                    if plan_to_check["valor"] >= customer_plan["valor_contrato"]:
                        suggested_plans.append(
                            schemas.SuggestedPlanOutSchema(
                                nome_plano_atual=customer_plan["nome"],
                                valor_plano_atual=customer_plan["valor_contrato"],
                                nome_plano_sugerido=plan_to_check["nome"],
                                valor_plano_sugerido=plan_to_check["valor"],
                            )
                        )
                        break

        return schemas.ListOutSchema[schemas.SuggestedPlanOutSchema](
            data=suggested_plans,
            meta=schemas.MetaOutSchema(
                total_itens=len(suggested_plans),
                pagina_atual=page,
                itens_por_pagina=items_per_page,
            ),
        )
