import json
from .. import SortOrder, ixc
from app.api.v1 import schemas
from pydantic import PositiveInt
from typing import Dict, Self, Optional


class FinanceiroIXCCliente(ixc.IXCCliente):
    async def get_contrato(self: Self, id_contrato: PositiveInt) -> Dict:
        grid_param = [{"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="cliente_contrato", payload=payload)
        return data

    async def get_faturas_abertas(
        self: Self,
        id_cliente: PositiveInt,
        page: Optional[PositiveInt] = 1,
        per_page: Optional[PositiveInt] = 15,
        sortname: Optional[str] = "fn_areceber.id",
        sortorder: Optional[SortOrder] = SortOrder.ASC,
    ) -> Dict:
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
        self: Self, id_contrato: PositiveInt
    ) -> Dict:
        payload = {"id_contrato": id_contrato}
        data = await self._make_request(
            endpoint="cliente_contrato_15464", payload=payload, include_ixcsoft=False
        )
        return data

    async def get_linha_digitavel(self: Self, id_fatura: PositiveInt) -> Dict:
        grid_param = [{"TB": "fn_areceber.id", "OP": "=", "P": str(id_fatura)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="fn_areceber", payload=payload)
        return data

    async def get_credenciais(self: Self, id_cliente: PositiveInt) -> Dict:
        grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id_cliente)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="cliente", payload=payload)
        return data

    async def put_clientes(
        self: Self, id_cliente: PositiveInt, cliente: schemas.ClienteUpdate
    ) -> Dict:
        data = await self._make_request(
            endpoint=f"cliente/{id_cliente}",
            payload=cliente,
            include_ixcsoft=False,
            method="PUT",
        )
        return data

    async def get_ultima_fatura_paga(self: Self, id_contrato: PositiveInt) -> Dict:
        grid_param = [
            {"TB": "fn_areceber.id_contrato", "OP": "=", "P": str(id_contrato)},
            {"TB": "fn_areceber.status", "OP": "=", "P": "R"},
        ]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
            "sortname": "fn_areceber.id",
            "sortorder": "DESC",
        }
        data = await self._make_request(endpoint="fn_areceber", payload=payload)
        return data
