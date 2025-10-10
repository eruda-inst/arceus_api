import json
from .. import ixc
from typing import Self, Dict
from app.api.v1 import schemas
from pydantic import PositiveInt


class TriagemIXCCliente(ixc.IXCCliente):
    """Cliente IXC para operações de triagem."""

    async def get_clientes(self: Self, id_cliente: PositiveInt) -> Dict:
        """
        Busca os dados de um cliente no IXC pelo ID.

        Args:
            id_cliente (PositiveInt): O ID do cliente a ser buscado.

        Returns:
            Dict: A resposta da API IXC contendo os dados do cliente.
        """
        grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id_cliente)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request("cliente", payload)
        return data

    async def put_clientes(
        self: Self, id_cliente: PositiveInt, cliente: schemas.ClienteUpdate
    ) -> Dict:
        """
        Atualiza os dados de um cliente no IXC.

        Args:
            id_cliente (PositiveInt): O ID do cliente a ser atualizado.
            cliente (schemas.ClienteUpdate): Os dados do cliente para atualização.

        Returns:
            Dict: A resposta da API IXC após a tentativa de atualização.
        """
        data = await self._make_request(
            endpoint=f"cliente/{id_cliente}",
            payload=cliente,
            include_ixcsoft=False,
            method="PUT",
        )
        return data
