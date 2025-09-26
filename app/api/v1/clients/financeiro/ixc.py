import json
from .. import SortOrder
from ..ixc import Cliente as IXCCliente
from typing import Dict, Any, List, Self, Optional


class Cliente(IXCCliente):
    async def get_faturas(
        self: Self,
        id_cliente: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "fn_areceber.id",
        sortorder: Optional[SortOrder] = SortOrder.ASC,
    ) -> List[Dict[str, Any]]:
        grid_param = [{"TB": "fn_areceber.id_cliente", "OP": "=", "P": str(id_cliente)}]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await self._make_request(endpoint="fn_areceber", payload=payload)
        return data

    async def get_contrato(self: Self, id_contrato: int) -> List[Dict[str, Any]]:
        grid_param = [{"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="cliente_contrato", payload=payload)
        return data
