import json
from typing import Any
from .. import ixc_client


class UpgradeIXCCliente(ixc_client.IXCCliente):
    @classmethod
    async def get_plano(cls, id_vd_contrato: int | str) -> Any:
        grid_param = [{"TB": "vd_contratos.id", "OP": "=", "P": str(id_vd_contrato)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await cls._make_request(endpoint="vd_contratos", payload=payload)
        return data

    @classmethod
    async def get_planos(cls, ids: list[int] | list[str]) -> Any:
        ids_str = (str(id) for id in ids)
        ids_str_tratados = str(",").join(ids_str)
        grid_param = [{"TB": "vd_contratos.id", "OP": "IN", "P": ids_str_tratados}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await cls._make_request(endpoint="vd_contratos", payload=payload)
        return data
