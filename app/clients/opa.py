import requests
from typing import Dict, Any
from ..core.config import settings
from fastapi import HTTPException, status


class OpaClient:
    def __init__(self):
        self.token = settings.OPA_TOKEN
        self.base_url = "https://newnet.opasuite.com.br/api/v1"
        self.headers = {"Authorization": f"Bearer {self.token}"}


    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        try:
            res = requests.get(url=url, headers=self.headers, json=payload)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro na API do OPA: {str(e)}"
            )


    def get_id_cliente_opa(self, protocolo_atendimento_opa: str) -> Dict[str, Any]:
        payload = {"filter": {"protocolo": protocolo_atendimento_opa}}
        data = self._make_request("atendimento", payload)
        return data


    def get_id_cliente_ixc(self, id_cliente_opa: str) -> Dict[str, Any]:
        payload = {"filter": {"_id": id_cliente_opa}}
        data = self._make_request("cliente", payload)
        return data