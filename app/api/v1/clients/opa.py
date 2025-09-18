import httpx
from ..core import settings
from fastapi import HTTPException, status
from typing import Dict, Any, Self, Optional


class OpaClient:
    def __init__(
        self: Self,
    ) -> None:
        self.token = settings.OPA_TOKEN
        self.base_url = "https://newnet.opasuite.com.br/api/v1"
        self.headers = {"Authorization": f"Bearer {self.token}"}

    async def _make_request(
        self: Self,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{endpoint}"
        try:
            async with httpx.AsyncClient(
                timeout=30.0,
            ) as async_client:
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

    async def get_id_cliente_opa(
        self: Self,
        protocolo: str,
    ) -> Optional[Dict[str, Any]]:
        payload = {"filter": {"protocolo": protocolo}}
        data = await self._make_request(
            endpoint="atendimento",
            payload=payload,
        )
        return data

    async def get_id_cliente_ixc(
        self: Self,
        id_cliente_opa: int,
    ) -> Optional[Dict[str, Any]]:
        payload = {"filter": {"_id": id_cliente_opa}}
        data = await self._make_request(
            endpoint="cliente",
            payload=payload,
        )
        return data
