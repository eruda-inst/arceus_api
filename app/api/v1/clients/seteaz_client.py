import httpx
from typing import Any
from app.api.v1 import cores
from pydantic import PositiveInt


class SeteAZCliente:
    base_url = cores.settings.base_url_7az
    api_key = cores.settings.api_key_7az.get_secret_value()
    timeout = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)
    async_client = httpx.AsyncClient(timeout=timeout)

    @classmethod
    def _get_headers(cls) -> Any:
        return {"X-API-Key": cls.api_key}

    @classmethod
    def _get_url(cls, endpoint: str) -> str:
        return f"{cls.base_url}/{endpoint}"

    @classmethod
    async def get_fatura(cls, id_fatura: PositiveInt) -> Any:
        url = cls._get_url(
            endpoint=f"v2/integrations/omnichannel/invoices/{id_fatura}/payment-data"
        )
        headers = cls._get_headers()
        res = await cls.async_client.request(method="GET", url=url, headers=headers)
        return res.json()

    @classmethod
    async def aclose(cls) -> None:
        await cls.async_client.aclose()
