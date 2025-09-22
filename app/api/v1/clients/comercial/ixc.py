import json
from typing import Dict, Any, Self, Optional, List
from app.api.v1.utils.enums import SortOrder
from ..ixc import Cliente as IXCCliente


class Cliente(IXCCliente):
    async def get_status_acesso(
        self: Self,
        id_contrato: int,
    ) -> Dict[str, Any]:
        grid_param = [
            {"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)},
        ]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
        }
        data = await self._make_request(endpoint="cliente_contrato", payload=payload)
        return data

    async def get_contratos(
        self: Self,
        id_cliente: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "cliente_contrato.id",
        sortorder: Optional[SortOrder] = SortOrder.ASC,
    ) -> List[Dict[str, Any]]:
        grid_param = [
            {"TB": "cliente_contrato.id_cliente", "OP": "=", "P": str(id_cliente)},
        ]
        payload = {
            "grid_param": json.dumps(
                obj=grid_param,
            ),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await self._make_request("cliente_contrato", payload)
        return data
