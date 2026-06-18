import json
from .. import ixc_client
from pydantic import PositiveInt


class UpgradeIXCCliente(ixc_client.IXCCliente):
    @classmethod
    async def get_plano(
        cls,
        grid_param: list[dict[str, str]] | None,
        page: PositiveInt | None = 1,
        per_page: PositiveInt | None = 10,
    ):
        payload = {
            "grid_param": json.dumps(obj=grid_param),
            "page": str(page),
            "rp": str(per_page),
        }
        data = await cls._make_request(endpoint="vd_contratos", payload=payload)
        return data
