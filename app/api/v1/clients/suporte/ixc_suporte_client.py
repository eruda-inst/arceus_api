import json
from typing import Any
from .. import ixc_client
from pydantic import PositiveInt
from app.api.v1 import schemas, utils


class SuporteIXCCliente(ixc_client.IXCCliente):
    @classmethod
    async def get_contratos(
        cls,
        id_cliente: PositiveInt,
        page: PositiveInt | None = 1,
        per_page: PositiveInt | None = 10,
        sortname: str | None = "cliente_contrato.id",
        sortorder: utils.SortOrder | None = utils.SortOrder.ASC,
    ) -> Any:
        grid_param = [
            {"TB": "cliente_contrato.id_cliente", "OP": "=", "P": str(id_cliente)},
            {"TB": "cliente_contrato.status", "OP": "!=", "P": "I"},
            {"TB": "cliente_contrato.status", "OP": "!=", "P": "N"},
            {"TB": "cliente_contrato.status", "OP": "!=", "P": "D"},
        ]
        payload: Any = {
            "grid_param": json.dumps(obj=grid_param),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await cls._make_request("cliente_contrato", payload)
        return data

    @classmethod
    async def get_status_conexao(cls, id_login: PositiveInt) -> Any:
        grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await cls._make_request("radusuarios", payload)
        return data

    @classmethod
    async def get_status_onu(
        cls,
        id_login: PositiveInt | None = None,
        mac_onu: str | None = None,
    ) -> Any:
        query_field = "id_login" if id_login else "mac"
        query_value = id_login if id_login else mac_onu
        grid_param = [
            {
                "TB": f"radpop_radio_cliente_fibra.{query_field}",
                "OP": "=",
                "P": str(query_value),
            }
        ]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await cls._make_request(
            endpoint="radpop_radio_cliente_fibra", payload=payload
        )
        return data

    @classmethod
    async def post_atendimentos(cls, atendimento: schemas.AtendimentoIn) -> Any:
        payload = atendimento.model_dump()
        return await cls._make_request(
            endpoint="su_ticket", payload=payload, include_ixcsoft=False
        )

    @classmethod
    async def post_desconectar_cliente(cls, id_login: PositiveInt) -> Any:
        payload = {"id": id_login}
        data = await cls._make_request(
            endpoint="desconectar_clientes", payload=payload, include_ixcsoft=False
        )
        return data

    @classmethod
    async def get_atendimentos(
        cls,
        id_login: PositiveInt,
        page: PositiveInt | None = 1,
        per_page: PositiveInt | None = 10,
        sortname: str | None = "su_ticket.id",
        sortorder: utils.SortOrder | None = utils.SortOrder.ASC,
    ) -> Any:
        grid_param = [
            {"TB": "su_ticket.id_login", "OP": "=", "P": str(id_login)},
            {"TB": "su_ticket.su_status", "OP": "!=", "P": "S"},
            {"TB": "su_ticket.su_status", "OP": "!=", "P": "C"},
        ]
        payload: Any = {
            "grid_param": json.dumps(obj=grid_param),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await cls._make_request(endpoint="su_ticket", payload=payload)
        return data

    @classmethod
    async def get_id_login(cls, id_contrato: PositiveInt) -> Any:
        grid_param = [
            {"TB": "radusuarios.id_contrato", "OP": "=", "P": str(id_contrato)}
        ]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await cls._make_request(endpoint="radusuarios", payload=payload)
        return data

    @classmethod
    async def get_onu_mac(cls, id_login: PositiveInt) -> Any:
        grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await cls._make_request(endpoint="radusuarios", payload=payload)
        return data

    @classmethod
    async def get_login(cls, id_login: PositiveInt) -> Any:
        grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await cls._make_request(endpoint="radusuarios", payload=payload)
        return data

    @classmethod
    async def put_ip(cls, id_login: PositiveInt, ip: Any) -> Any:
        data = await cls._make_request(
            endpoint=f"radusuarios/{id_login}",
            payload=ip,
            include_ixcsoft=False,
            method="PUT",
        )
        return data

    @classmethod
    async def post_limpar_mac(cls, id_login: PositiveInt) -> Any:
        payload = {"get_id": id_login}
        data = await cls._make_request(
            endpoint="radusuarios_25452", payload=payload, include_ixcsoft=False
        )
        return data

    @classmethod
    async def get_dados_wifi(cls, id_login: PositiveInt) -> Any:
        grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await cls._make_request(endpoint="radusuarios", payload=payload)
        return data
