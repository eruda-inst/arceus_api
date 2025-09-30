import json
from .. import SortOrder
from ..ixc import IXCCliente
from pydantic import PositiveInt
from typing import Dict, Any, List, Self, Optional


class FinanceiroIXCCliente(IXCCliente):
    async def get_contrato(self: Self, id_contrato: int) -> List[Dict[str, Any]]:
        grid_param = [{"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="cliente_contrato", payload=payload)
        return data

    async def get_faturas_abertas(
        self: Self,
        id_cliente: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "fn_areceber.id",
        sortorder: Optional[SortOrder] = SortOrder.ASC,
    ) -> List[Dict[str, Any]]:
        grid_param = [
            {"TB": "fn_areceber.id_cliente", "OP": "=", "P": str(id_cliente)},
            {"TB": "fn_areceber.status", "OP": "=", "P": "A"},
        ]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await self._make_request(endpoint="fn_areceber", payload=payload)
        return data

    async def post_desbloqueio_em_confianca(
        self: Self, id_contrato: int
    ) -> Dict[str, Any]:
        payload = {"id_contrato": id_contrato}
        data = await self._make_request(
            endpoint="cliente_contrato_15464", payload=payload, include_ixcsoft=False
        )
        return data

    async def get_linha_digitavel(self: Self, id: PositiveInt) -> List[Dict[str, Any]]:
        grid_param = [{"TB": "fn_areceber.id", "OP": "=", "P": str(id)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="fn_areceber", payload=payload)
        return data
