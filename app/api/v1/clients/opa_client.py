import httpx
from .. import cores
from typing import Any
from pydantic import PositiveInt
from fastapi import HTTPException, status


class OpaCliente:
    token = cores.settings.OPA_TOKEN
    host = cores.settings.OPA_HOST
    base_url = f"https://{host}/api/v1"
    headers = {"Authorization": f"Bearer {token}"}

    @classmethod
    async def _make_request(cls, endpoint: str, payload: Any) -> Any:
        url = f"{cls.base_url}/{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as async_client:
                res = await async_client.request(
                    method="GET",
                    url=url,
                    headers=cls.headers,
                    json=payload,
                )
                res.raise_for_status()
                return res.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro na API do OPA: {str(e)}",
            )

    @classmethod
    async def get_id_cliente_opa(cls, protocolo: str) -> Any:
        payload = {"filter": {"protocolo": protocolo}}
        data = await cls._make_request(endpoint="atendimento", payload=payload)
        return data

    @classmethod
    async def get_id_cliente_ixc(cls, id_cliente_opa: PositiveInt) -> Any:
        payload = {"filter": {"_id": id_cliente_opa}}
        data = await cls._make_request(endpoint="cliente", payload=payload)
        return data

    @classmethod
    async def cliente_existe(cls, cpf_cnpj_limpo: str) -> bool:
        payload: Any = {"filter": {"cpf_cnpj": cpf_cnpj_limpo}, "options": {"limit": 1}}
        data = await cls()._make_request(endpoint="cliente", payload=payload)
        if data.get("data"):
            return True
        return False
