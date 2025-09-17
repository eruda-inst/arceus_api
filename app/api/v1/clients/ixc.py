import json
import httpx
import base64
from ..core import settings
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
        include_ixcsoft: bool = True,
    ) -> Dict[str, str]:
        headers = {"Authorization": self.auth_header}
        if include_ixcsoft:
            headers["ixcsoft"] = "listar"
        return headers

    async def _make_request(
        self: Self,
        endpoint: str,
        payload: Dict[str, Any],
        include_ixcsoft: bool = True,
    ) -> Optional[Union[List[Dict[str, Any]], Dict[str, Any]]]:
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers(include_ixcsoft)
        try:
            async with httpx.AsyncClient(timeout=30.0) as async_client:
                res = await async_client.request(method="POST", url=url, headers=headers, json=payload)
                res.raise_for_status()
                return res.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Falha na comunicação com o serviço IXC"
            ) from e
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro retornado pelo IXC: {e.response.text}"
            ) from e
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Resposta inválida do servidor IXC"
            ) from e

    async def get_contratos(
        self: Self,
        id_cliente: int,
        page: int = 1,
        per_page: int = 10,
    ) -> Optional[List[Dict[str, Any]]]:
        grid_param = [{
            "TB": "cliente_contrato.id_cliente",
            "OP": "=",
            "P": str(id_cliente),
        }]
        payload = {
            "grid_param": json.dumps(grid_param),
            "page": page,
            "rp": per_page,
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
            "grid_param": json.dumps(grid_param),
        }
        data = await self._make_request("radusuarios", payload)
        return data

    async def get_status_onu(
        self: Self,
        id_login: int,
        mac_onu: str,
    ) -> Optional[Dict[str, Any]]:
        query_field = "id_login" if id_login else "mac"
        query_value = id_login if id_login else mac_onu
        grid_param = [{
            "TB": f"radpop_radio_cliente_fibra.{query_field}",
            "OP": "=",
            "P": str(query_value),
        }]
        payload = {
            "grid_param": json.dumps(grid_param),
        }
        data = await self._make_request("radpop_radio_cliente_fibra", payload)
        return data

    async def post_atendimentos(
        self: Self,
        atendimento: AtendimentoIn,
    ) -> None:
        payload = atendimento.model_dump()
        await self._make_request("su_ticket", payload, include_ixcsoft=False)

    async def post_desconectar_cliente(
        self: Self,
        id_login: int,
    ) -> None:
        payload = {"id": id_login}
        await self._make_request("desconectar_clientes", payload, include_ixcsoft=False)

    async def get_atendimentos(
        self: Self,
        id_login: int,
        page: int = 1,
        per_page: int = 10,
    ) -> Optional[List[Dict[str, Any]]]:
        grid_param = [{
            "TB": "su_ticket.id_login",
            "OP": "=",
            "P": str(id_login),
        }]
        payload = {
            "grid_param": json.dumps(grid_param),
            "page": page,
            "rp": per_page,
        }
        data = await self._make_request("su_ticket", payload)
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
            "grid_param": json.dumps(grid_param),
        }
        data = await self._make_request("fn_areceber", payload)
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
            "grid_param": json.dumps(grid_param),
        }
        data = await self._make_request("radusuarios", payload)
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
            "grid_param": json.dumps(grid_param),
        }
        data = await self._make_request("radusuarios", payload)
        return data