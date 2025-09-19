import json
import httpx
import base64
from ..core import settings
from ..utils import SortOrder
from ..schemas import AtendimentoIn
from fastapi import HTTPException, status
from typing import Dict, Any, List, Union, Self, Optional


class IXCClient:
    def __init__(
        self: Self,
    ) -> None:
        self.token = settings.IXC_TOKEN
        self.base_url = "https://ixc.newnet.com.br/webservice/v1"
        self.auth_header = self._create_auth_header()

    def _create_auth_header(
        self: Self,
    ) -> str:
        token_encoded = base64.b64encode(self.token.encode("utf-8")).decode("utf-8")
        return f"Basic {token_encoded}"

    def _get_headers(
        self: Self,
        include_ixcsoft: Optional[bool] = True,
    ) -> Dict[str, str]:
        headers = {"Authorization": self.auth_header}
        if include_ixcsoft:
            headers["ixcsoft"] = "listar"
        return headers

    async def _make_request(
        self: Self,
        endpoint: str,
        payload: Dict[str, Any],
        include_ixcsoft: Optional[bool] = True,
    ) -> Optional[Union[List[Dict[str, Any]], Dict[str, Any]]]:
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers(
            include_ixcsoft=include_ixcsoft,
        )
        try:
            async with httpx.AsyncClient(
                timeout=30.0,
            ) as async_client:
                res = await async_client.request(
                    method="POST",
                    url=url,
                    headers=headers,
                    json=payload,
                )
                res.raise_for_status()
                return res.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Falha na comunicação com o serviço IXC: {e.response.text}"
            ) from e
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro retornado pelo IXC: {e.response.text}"
            ) from e
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resposta inválida do servidor IXC: {e}"
            ) from e

    # == SUPORTE ==

    async def get_contratos_ativos(
        self: Self,
        id_cliente: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "cliente_contrato.id",
        sortorder: Optional[SortOrder] = SortOrder.ASC,
    ) -> Optional[List[Dict[str, Any]]]:
        grid_param = [
            { "TB": "cliente_contrato.id_cliente", "OP": "=", "P": str(id_cliente) },
            { "TB": "cliente_contrato.status", "OP": "!=", "P": "I" },
            { "TB": "cliente_contrato.status", "OP": "!=", "P": "N" },
            { "TB": "cliente_contrato.status", "OP": "!=", "P": "D" },
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
        grid_param = [{
            "TB": "radusuarios.id",
            "OP": "=",
            "P": str(id_login),
        }]
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
        grid_param = [{
            "TB": f"radpop_radio_cliente_fibra.{query_field}", "OP": "=", "P": str(query_value),
        }]
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
        sortorder: Optional[SortOrder] = SortOrder.ASC
    ) -> Optional[List[Dict[str, Any]]]:
        grid_param = [
            { "TB": "su_ticket.id_login", "OP": "=", "P": str(id_login) },
            { "TB": "su_ticket.su_status", "OP": "!=", "P": "S" },
            { "TB": "su_ticket.su_status", "OP": "!=", "P": "C" },
        ]
        payload = {
            "grid_param": json.dumps(
                obj=grid_param,
            ),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder
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
        grid_param = [{
            "TB": "fn_areceber.id_contrato",
            "OP": "=",
            "P": str(id_contrato),
        }]
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
        grid_param = [{
            "TB": "radusuarios.id_contrato",
            "OP": "=",
            "P": str(id_contrato),
        }]
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
        grid_param = [{
            "TB": "radusuarios.id",
            "OP": "=",
            "P": str(id_login),
        }]
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
        sortorder: Optional[SortOrder] = SortOrder.ASC
    ) -> Optional[List[Dict[str, Any]]]:
        grid_param = [
            { "TB": "su_ticket.id_login", "OP": "=", "P": str(id_login) },
            { "TB": "su_ticket.su_status", "OP": "!=", "P": "P" },
            { "TB": "su_ticket.su_status", "OP": "!=", "P": "EP" },
            { "TB": "su_ticket.su_status", "OP": "!=", "P": "S" },
            { "TB": "su_ticket.su_status", "OP": "!=", "P": "C" },
            { "TB": "su_ticket.id_responsavel_tecnico", "OP": "=", "P": "14336"}
        ]
        payload = {
            "grid_param": json.dumps(
                obj=grid_param,
            ),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder
        }
        data = await self._make_request(
            endpoint="su_ticket",
            payload=payload,
        )
        return data

    # == COMERCIAL ==

    async def get_status_acesso():
        #status_internet
        pass