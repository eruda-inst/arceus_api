import json
from typing import Any
from .. import ixc_client


class UpgradeIXCCliente(ixc_client.IXCCliente):
    @classmethod
    async def get_plano(cls, grid_param: list[dict[str, str]] | None):
        payload: Any = {"grid_param": json.dumps(obj=grid_param)}
        data = await cls._make_request(endpoint="vd_contratos", payload=payload)
        return data
