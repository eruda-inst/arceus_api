import json
from typing import Any
from .. import ixc_client
from app.api.v1 import schemas
from pydantic import PositiveInt


class TriagemIXCCliente(ixc_client.IXCCliente):
    async def get_clientes(self, id_cliente: PositiveInt) -> Any:
        grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id_cliente)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request("cliente", payload)
        return data

    async def put_clientes(
        self, id_cliente: PositiveInt, cliente: schemas.ClienteUpdate
    ) -> Any:
        data = await self._make_request(
            endpoint=f"cliente/{id_cliente}",
            payload=cliente,
            include_ixcsoft=False,
            method="PUT",
        )
        return data
