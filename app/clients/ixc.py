import httpx
import base64
from ..core import settings
from typing import Dict, Any, List
from ..schemas import AtendimentoIn
from fastapi import HTTPException, status


class IXCClient:
    def __init__(
        self,
    ) -> None:
        self.token = settings.IXC_TOKEN
        self.base_url = "https://ixc.newnet.com.br/webservice/v1"
        self.auth_header = self._create_auth_header()

    def _create_auth_header(
        self,
    ) -> str:
        token_encoded = base64.b64encode(self.token.encode("utf-8")).decode("utf-8")
        return f"Basic {token_encoded}"

    def _get_headers(
        self,
        include_ixcsoft: bool = True,
    ) -> Dict[str, str]:
        headers = {"Authorization": self.auth_header}
        if include_ixcsoft:
            headers["ixcsoft"] = "listar"
        return headers

    async def _make_request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        include_ixcsoft: bool = True,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers(include_ixcsoft)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url=url, headers=headers, json=payload)
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

    async def get_contratos_ativos_cliente(
        self,
        id_cliente_ixc: int,
        page: int = 1,
        per_page: int = 1,
    ) -> List[Dict[str, Any]]:
        payload = {
            "qtype": "cliente_contrato.id_cliente",
            "query": id_cliente_ixc,
            "oper": "=",
            "page": page,
            "rp": per_page
        }
        data = await self._make_request("cliente_contrato", payload)
        return data

    async def get_status_conexao(
        self,
        id_login_ixc: int,
    ) -> List[Dict[str, Any]]:
        payload = {
            "qtype": "radusuarios.id",
            "query": id_login_ixc,
            "oper": "=",
        }
        data = await self._make_request("radusuarios", payload)
        return data

    async def get_status_contrato(
        self,
        id_contrato_ixc: int,
    ) -> Dict[str, Any]:
        payload = {
            "qtype": "cliente_contrato.id",
            "query": id_contrato_ixc,
            "oper": "=",
        }
        data = await self._make_request("cliente_contrato", payload)
        return data

    async def get_status_onu(
        self,
        id_login_ixc: int,
        mac_onu_ixc: str,
    ) -> Dict[str, Any]:
        query_field = "id_login" if id_login_ixc else "mac"
        query_value = id_login_ixc if id_login_ixc else mac_onu_ixc
        payload = {
            "qtype": f"radpop_radio_cliente_fibra.{query_field}",
            "query": query_value,
            "oper": "=",
        }
        data = await self._make_request("radpop_radio_cliente_fibra", payload)
        return data

    async def valor_e_data_vencimento(
        self,
        id_contrato_ixc: int,
    ) -> Dict[str, Any]:
        payload = {
            "qtype": "fn_areceber.id_contrato",
            "query": id_contrato_ixc,
            "oper": "="
        }
        data = await self._make_request("fn_areceber", payload)
        return data
    
    async def abrir_atendimento(
        self,
        atendimento: AtendimentoIn,
    ) -> None:
        payload = atendimento.model_dump()
        await self._make_request("su_ticket", payload, include_ixcsoft=False)
    
    async def enviar_sinal_desconexao(
        self,
        id_login_ixc: int,
    ) -> None:
        payload = {"id": id_login_ixc}
        await self._make_request("desconectar_clientes", payload, include_ixcsoft=False)

    async def checar_atendimentos_abertos(
        self,
        id_login_ixc: int,
        page: int = 1,
        per_page: int = 10,
    ) -> List[Dict[str, Any]]:
        payload = {
            "qtype": "su_ticket.id_login",
            "query": id_login_ixc,
            "oper": "=",
            "page": page,
            "rp": per_page
        }
        data = await self._make_request("su_ticket", payload)
        return data