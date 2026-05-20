import json
from .. import ixc_client
from typing import Any, Dict
from pydantic import PositiveInt
from app.api.v1 import schemas, utils


class ComercialIXCCliente(ixc_client.IXCCliente):
    async def get_status_acesso(self, id_contrato: int) -> Any:
        grid_param = [{"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="cliente_contrato", payload=payload)
        return data

    async def get_contratos(
        self,
        id_cliente: PositiveInt,
        page: PositiveInt | None = 1,
        per_page: PositiveInt | None = 10,
        sortname: str | None = "cliente_contrato.id",
        sortorder: utils.SortOrder | None = utils.SortOrder.ASC,
    ) -> Any:
        grid_param = [
            {"TB": "cliente_contrato.id_cliente", "OP": "=", "P": str(id_cliente)}
        ]
        payload: Any = {
            "grid_param": json.dumps(obj=grid_param),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await self._make_request(endpoint="cliente_contrato", payload=payload)
        return data

    async def post_leads(self, lead: schemas.LeadIn) -> Any:
        payload = lead.model_dump()
        """
        Este campo "data_cadastro" é obrigatório na API do IXC (temos que mandar alguma coisa), porém o que é mandado é descartado e a data é gerada automaticamente pela própria API deles.

        Só mais uma esquisitice da API do IXC.
        """
        payload["data_cadastro"] = "N/A"
        data = await self._make_request(
            endpoint="contato", payload=payload, include_ixcsoft=False
        )
        return data

    async def get_login(self, id_cliente: PositiveInt) -> Any:
        grid_param = [{"TB": "radusuarios.id_cliente", "OP": "=", "P": str(id_cliente)}]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
        }
        data = await self._make_request(endpoint="radusuarios", payload=payload)
        return data

    async def get_lead_by_cpf_cnpj(self, cnpj_cpf: str) -> Any:
        grid_param = [{"TB": "contato.cnpj_cpf", "OP": "=", "P": cnpj_cpf}]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
        }
        data = await self._make_request(endpoint="contato", payload=payload)
        return data

    async def put_lead(self, lead_id: int, lead: Dict[str, Any]) -> Any:
        """
        Este campo "data_cadastro" é obrigatório na API do IXC (temos que mandar alguma coisa), porém o que é mandado é descartado e a data é gerada automaticamente pela própria API deles.

        Só mais uma esquisitice da API do IXC.
        """
        data = await self._make_request(
            endpoint=f"contato/{lead_id}",
            payload=lead,
            method="PUT",
            include_ixcsoft=False,
        )
        return data
