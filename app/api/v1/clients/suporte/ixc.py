import json
from .. import ixc
from app.api.v1 import schemas, utils
from typing import Any, Self, Optional


class SuporteIXCCliente(ixc.IXCCliente):
    async def get_contratos(
        self: Self,
        id_cliente: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "cliente_contrato.id",
        sortorder: Optional[utils.SortOrder] = utils.SortOrder.ASC,
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
        data = await self._make_request("cliente_contrato", payload)
        return data

    async def get_status_conexao(self: Self, id_login: int) -> Any:
        grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request("radusuarios", payload)
        return data

    async def get_status_onu(
        self: Self, id_login: Optional[int] = None, mac_onu: Optional[str] = None
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
        data = await self._make_request(
            endpoint="radpop_radio_cliente_fibra", payload=payload
        )
        return data

    async def post_atendimentos(self: Self, atendimento: schemas.AtendimentoIn) -> Any:
        payload = atendimento.model_dump()
        return await self._make_request(
            endpoint="su_ticket", payload=payload, include_ixcsoft=False
        )

    async def post_desconectar_cliente(self: Self, id_login: int) -> Any:
        payload = {"id": id_login}
        data = await self._make_request(
            endpoint="desconectar_clientes", payload=payload, include_ixcsoft=False
        )
        return data

    async def get_atendimentos(
        self: Self,
        id_login: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "su_ticket.id",
        sortorder: Optional[utils.SortOrder] = utils.SortOrder.ASC,
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
        data = await self._make_request(endpoint="su_ticket", payload=payload)
        return data

    async def get_id_login(self: Self, id_contrato: int) -> Any:
        grid_param = [
            {"TB": "radusuarios.id_contrato", "OP": "=", "P": str(id_contrato)}
        ]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="radusuarios", payload=payload)
        return data

    async def get_onu_mac(self: Self, id_login: int) -> Any:
        grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="radusuarios", payload=payload)
        return data

    async def get_login(self: Self, id_login: int) -> Any:
        grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="radusuarios", payload=payload)
        return data

    async def put_ip(self: Self, id_login: int, ip: schemas.IPUpdate) -> Any:
        data = await self._make_request(
            endpoint=f"radusuarios/{id_login}",
            payload=ip,
            include_ixcsoft=False,
            method="PUT",
        )
        return data

    async def post_limpar_mac(self: Self, id_login: int) -> Any:
        payload = {"get_id": id_login}
        data = await self._make_request(
            endpoint="radusuarios_25452", payload=payload, include_ixcsoft=False
        )
        return data
