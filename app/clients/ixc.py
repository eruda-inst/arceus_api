import httpx
import base64
from fastapi import HTTPException, status
from app.core.config import settings
from typing import Dict, Any, List


class IXCClient:
    def __init__(self) -> None:
        self.token = settings.IXC_TOKEN
        self.base_url = "https://ixc.newnet.com.br/webservice/v1"
        self.headers = self._create_headers()


    def _create_headers(self) -> Dict[str, str]:
        token_encoded = base64.b64encode(self.token.encode("utf-8")).decode("utf-8")
        return {
            "ixcsoft": "listar",
            "Authorization": f"Basic {token_encoded}",
        }


    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        try:
            with httpx.Client(timeout=30.0) as client:
                res = client.post(url, headers=self.headers, json=payload)
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


    def get_contratos_cliente(self, id_cliente_ixc: str) -> List[Dict[str, Any]]:
        payload = {
            "qtype": "cliente_contrato.id_cliente",
            "query": id_cliente_ixc,
            "oper": "=",
        }
        data = self._make_request("cliente_contrato", payload)
        return data
    

    def get_status_conexao(self, id_login_ixc: int)-> List[Dict[str, Any]]:
        payload = {
            "qtype": "radusuarios.id",
            "query": id_login_ixc,
            "oper": "=",
        }
        data = self._make_request("radusuarios", payload)
        return data