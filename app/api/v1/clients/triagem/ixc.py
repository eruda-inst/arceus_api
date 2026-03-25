import json
from .. import ixc
from typing import Self, Dict
from app.api.v1 import schemas
from pydantic import PositiveInt


class TriagemIXCCliente(ixc.IXCCliente):
    async def get_clientes(self: Self, id_cliente: PositiveInt) -> Dict:
        grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id_cliente)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request("cliente", payload)
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
