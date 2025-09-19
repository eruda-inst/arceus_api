import json
from ..ixc import Cliente as IXCCliente
from typing import Dict, Any, Self, Optional


class Cliente(IXCCliente):
    async def get_status_acesso(
        self: Self,
        id_contrato: int,
    ) -> Optional[Dict[str, Any]]:
        grid_param = [
            {"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)},
        ]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
        }
        data = await self._make_request(endpoint="cliente_contrato", payload=payload)
        return data