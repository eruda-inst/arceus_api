from ..opa import Cliente as OpaCliente
from typing import Dict, Any, Self, Optional


class Cliente(OpaCliente):
    async def get_id_cliente_opa(
        self: Self, protocolo: str
    ) -> Optional[Dict[str, Any]]:
        payload = {"filter": {"protocolo": protocolo}}
        data = await self._make_request(endpoint="atendimento", payload=payload)
        return data

    async def get_id_cliente_ixc(
        self: Self, id_cliente_opa: int
    ) -> Optional[Dict[str, Any]]:
        payload = {"filter": {"_id": id_cliente_opa}}
        data = await self._make_request(endpoint="cliente", payload=payload)
        return data
