import json
from typing import Any
from app.api.v1 import schemas
from pydantic import PositiveInt
from .. import SortOrder, ixc_client


class FinanceiroIXCCliente(ixc_client.IXCCliente):
    @classmethod
    async def get_contrato(cls, id_contrato: PositiveInt) -> Any:
        grid_param = [{"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await cls._make_request(endpoint="cliente_contrato", payload=payload)
        return data

    @classmethod
    async def get_faturas_abertas(
        cls,
        id_cliente: PositiveInt,
        page: PositiveInt | None = 1,
        per_page: PositiveInt | None = 15,
        sortname: str | None = "fn_areceber.id",
        sortorder: SortOrder | None = SortOrder.ASC,
    ) -> Any:
        grid_param = [
            {"TB": "fn_areceber.id_cliente", "OP": "=", "P": str(id_cliente)},
            {"TB": "fn_areceber.status", "OP": "=", "P": "A"},
        ]
        payload: Any = {
            "grid_param": json.dumps(obj=grid_param),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await cls._make_request(endpoint="fn_areceber", payload=payload)
        return data

    @classmethod
    async def post_desbloqueio_em_confianca(cls, id_contrato: PositiveInt) -> Any:
        payload = {"id": id_contrato}
        data = await cls._make_request(
            endpoint="desbloqueio_confianca", payload=payload, include_ixcsoft=False
        )
        return data

    @classmethod
    async def get_linha_digitavel(cls, id_fatura: PositiveInt) -> Any:
        grid_param = [{"TB": "fn_areceber.id", "OP": "=", "P": str(id_fatura)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await cls._make_request(endpoint="fn_areceber", payload=payload)
        return data

    @classmethod
    async def get_credenciais(cls, id_cliente: PositiveInt) -> Any:
        grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id_cliente)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await cls._make_request(endpoint="cliente", payload=payload)
        return data

    @classmethod
    async def put_clientes(
        cls, id_cliente: PositiveInt, cliente: schemas.ClienteUpdate
    ) -> Any:
        data = await cls._make_request(
            endpoint=f"cliente/{id_cliente}",
            payload=cliente,
            include_ixcsoft=False,
            method="PUT",
        )
        return data

    @classmethod
    async def get_ultima_fatura_paga(cls, id_contrato: PositiveInt) -> Any:
        grid_param = [
            {"TB": "fn_areceber.id_contrato", "OP": "=", "P": str(id_contrato)},
            {"TB": "fn_areceber.status", "OP": "=", "P": "R"},
        ]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
            "sortname": "fn_areceber.id",
            "sortorder": "DESC",
        }
        data = await cls._make_request(endpoint="fn_areceber", payload=payload)
        return data
