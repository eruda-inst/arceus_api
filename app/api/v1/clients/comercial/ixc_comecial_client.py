import json
from .. import ixc_client
from pydantic import PositiveInt
from app.api.v1 import schemas, utils
from typing import Any, Self, Optional


class ComercialIXCCliente(ixc_client.IXCCliente):
    async def get_status_acesso(self: Self, id_contrato: int) -> Any:

        grid_param = [{"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="cliente_contrato", payload=payload)
        return data

    async def get_contratos(
        self: Self,
        id_cliente: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "cliente_contrato.id",
        sortorder: Optional[utils.SortOrder] = utils.SortOrder.ASC,
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

    async def post_leads(self: Self, lead: schemas.LeadIn) -> Any:
        payload = lead.model_dump()
        data = await self._make_request(
            endpoint="contato", payload=payload, include_ixcsoft=False
        )
        return data

    async def get_login(self: Self, id_cliente: PositiveInt) -> Any:
        grid_param = [{"TB": "radusuarios.id_cliente", "OP": "=", "P": str(id_cliente)}]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
        }
        data = await self._make_request(endpoint="radusuarios", payload=payload)
        return data
