import json
from .. import SortOrder
from .. import AtendimentoIn
from ..ixc import Cliente as IXCCliente
from typing import Dict, Any, List, Self, Optional


class Cliente(IXCCliente):
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
            "grid_param": json.dumps(
                obj=grid_param,
            ),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await self._make_request("cliente_contrato", payload)
        return data

    async def get_status_conexao(
        self: Self,
        id_login: int,
    ) -> Optional[List[Dict[str, Any]]]:
        grid_param = [
            {
                "TB": "radusuarios.id",
                "OP": "=",
                "P": str(id_login),
            }
        ]
        payload = {
            "grid_param": json.dumps(
                obj=grid_param,
            ),
        }
        data = await self._make_request("radusuarios", payload)
        return data

    async def get_status_onu(
        self: Self,
        id_login: Optional[int] = None,
        mac_onu: Optional[str] = None,
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
        payload = {
            "grid_param": json.dumps(
                obj=grid_param,
            ),
        }
        data = await self._make_request(
            endpoint="radpop_radio_cliente_fibra",
            payload=payload,
        )
        return data

    async def post_atendimentos(
        self: Self,
        atendimento: AtendimentoIn,
    ) -> None:
        payload = atendimento.model_dump()
        await self._make_request(
            endpoint="su_ticket",
            payload=payload,
            include_ixcsoft=False,
        )

    async def post_desconectar_cliente(
        self: Self,
        id_login: int,
    ) -> None:
        payload = {"id": id_login}
        await self._make_request(
            endpoint="desconectar_clientes",
            payload=payload,
            include_ixcsoft=False,
        )

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
            "grid_param": json.dumps(
                obj=grid_param,
            ),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await self._make_request(
            endpoint="su_ticket",
            payload=payload,
        )
        return data

    async def get_valor_e_data_vencimento(
        self: Self,
        id_contrato: int,
    ) -> Optional[Dict[str, Any]]:
        grid_param = [
            {
                "TB": "fn_areceber.id_contrato",
                "OP": "=",
                "P": str(id_contrato),
            }
        ]
        payload = {
            "grid_param": json.dumps(
                obj=grid_param,
            ),
        }
        data = await self._make_request(
            endpoint="fn_areceber",
            payload=payload,
        )
        return data

    async def get_id_login(
        self: Self,
        id_contrato: int,
    ) -> Optional[Dict[str, Any]]:
        grid_param = [
            {
                "TB": "radusuarios.id_contrato",
                "OP": "=",
                "P": str(id_contrato),
            }
        ]
        payload = {
            "grid_param": json.dumps(
                obj=grid_param,
            ),
        }
        data = await self._make_request(
            endpoint="radusuarios",
            payload=payload,
        )
        return data

    async def get_onu_mac(
        self: Self,
        id_login: int,
    ) -> Optional[Dict[str, Any]]:
        grid_param = [
            {
                "TB": "radusuarios.id",
                "OP": "=",
                "P": str(id_login),
            }
        ]
        payload = {
            "grid_param": json.dumps(
                obj=grid_param,
            ),
        }
        data = await self._make_request(
            endpoint="radusuarios",
            payload=payload,
        )
        return data

    async def get_id_atendimento_aberto(
        self: Self,
        id_login: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "su_ticket.id",
        sortorder: Optional[SortOrder] = SortOrder.ASC,
    ) -> Optional[List[Dict[str, Any]]]:
        grid_param = [
            {"TB": "su_ticket.id_login", "OP": "=", "P": str(id_login)},
            {"TB": "su_ticket.su_status", "OP": "!=", "P": "P"},
            {"TB": "su_ticket.su_status", "OP": "!=", "P": "EP"},
            {"TB": "su_ticket.su_status", "OP": "!=", "P": "S"},
            {"TB": "su_ticket.su_status", "OP": "!=", "P": "C"},
            {"TB": "su_ticket.id_responsavel_tecnico", "OP": "=", "P": "14336"},
        ]
        payload = {
            "grid_param": json.dumps(
                obj=grid_param,
            ),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await self._make_request(
            endpoint="su_ticket",
            payload=payload,
        )
        return data
