import json
from .. import SortOrder, AtendimentoIn
from ..ixc import IXCCliente
from app.api.v1 import schemas
from typing import Dict, Any, List, Self, Optional


class SuporteIXCCliente(IXCCliente):
    async def get_contratos_ativos(
        self: Self,
        id_cliente: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "cliente_contrato.id",
        sortorder: Optional[SortOrder] = SortOrder.ASC,
    ) -> Optional[List[Dict[str, Any]]]:
        grid_param = [
            {"TB": "cliente_contrato.id_cliente", "OP": "=", "P": str(id_cliente)},
            {"TB": "cliente_contrato.status", "OP": "!=", "P": "I"},
            {"TB": "cliente_contrato.status", "OP": "!=", "P": "N"},
            {"TB": "cliente_contrato.status", "OP": "!=", "P": "D"},
        ]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await self._make_request("cliente_contrato", payload)
        return data

    async def get_status_conexao(
        self: Self, id_login: int
    ) -> Optional[List[Dict[str, Any]]]:
        grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request("radusuarios", payload)
        return data

    async def get_status_onu(
        self: Self, id_login: Optional[int] = None, mac_onu: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
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

    async def post_atendimentos(self: Self, atendimento: AtendimentoIn) -> None:
        payload = atendimento.model_dump()
        return await self._make_request(
            endpoint="su_ticket", payload=payload, include_ixcsoft=False
        )

    async def post_desconectar_cliente(self: Self, id_login: int) -> Dict[str, Any]:
        payload = {"id": id_login}
        data = await self._make_request(
            endpoint="desconectar_clientes", payload=payload, include_ixcsoft=False
        )
        return data

    async def get_atendimentos_abertos(
        self: Self,
        id_login: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "su_ticket.id",
        sortorder: Optional[SortOrder] = SortOrder.ASC,
    ) -> Optional[List[Dict[str, Any]]]:
        grid_param = [
            {"TB": "su_ticket.id_login", "OP": "=", "P": str(id_login)},
            {"TB": "su_ticket.su_status", "OP": "!=", "P": "S"},
            {"TB": "su_ticket.su_status", "OP": "!=", "P": "C"},
        ]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await self._make_request(endpoint="su_ticket", payload=payload)
        return data

    async def get_id_login(self: Self, id_contrato: int) -> Optional[Dict[str, Any]]:
        grid_param = [
            {"TB": "radusuarios.id_contrato", "OP": "=", "P": str(id_contrato)}
        ]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="radusuarios", payload=payload)
        return data

    async def get_onu_mac(self: Self, id_login: int) -> Optional[Dict[str, Any]]:
        grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="radusuarios", payload=payload)
        return data

    async def get_login(self: Self, id: int) -> Optional[Dict[str, Any]]:
        grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="radusuarios", payload=payload)
        return data

    async def put_ip(
        self: Self, id: int, ip: schemas.IPUpdate
    ) -> Optional[Dict[str, Any]]:
        data = await self._make_request(
            endpoint=f"radusuarios/{id}",
            payload=ip,
            include_ixcsoft=False,
            method="PUT",
        )
        return data

    async def post_limpar_mac(self: Self, id_login: int) -> None:
        payload = {"get_id": id_login}
        data = await self._make_request(
            endpoint="radusuarios_25452", payload=payload, include_ixcsoft=False
        )
        return data
