import httpx
from .. import core
from typing import Dict, Self
from fastapi import HTTPException, status


class OpaCliente:
    def __init__(self: Self) -> None:
        self.token = core.settings.OPA_TOKEN
        self.host = core.settings.OPA_HOST
        self.base_url = f"https://{self.host}/api/v1"
        self.headers = {"Authorization": f"Bearer {self.token}"}

    async def _make_request(self: Self, endpoint: str, payload: Dict) -> Dict:
        url = f"{self.base_url}/{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as async_client:
                res = await async_client.request(
                    method="GET",
                    url=url,
                    headers=self.headers,
                    json=payload,
                )
                res.raise_for_status()
                return res.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro na API do OPA: {str(e)}",
            )

    async def get_id_cliente_opa(self: Self, protocolo: str) -> Dict:
        payload = {"filter": {"protocolo": protocolo}}
        data = await self._make_request(endpoint="atendimento", payload=payload)
        return data

    async def get_id_cliente_ixc(self: Self, id_cliente_opa: int) -> Dict:
        payload = {"filter": {"_id": id_cliente_opa}}
        data = await self._make_request(endpoint="cliente", payload=payload)
        return data
