import httpx
from typing import Any
from app.api.v1 import cores
from pydantic import PositiveInt


class SeteAZCliente:
    base_url = cores.settings.BASE_URL_7AZ
    api_key = cores.settings.API_KEY_7AZ
    timeout = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)
    async_client = httpx.AsyncClient(timeout=timeout)

    @classmethod
    def _get_headers(cls) -> Any:
        return {"X-API-Key": cls.api_key}

    @classmethod
    def _get_url(cls, endpoint: str) -> str:
        return f"{cls.base_url}/{endpoint}"

    @classmethod
    async def get_chave_pix(cls, id_fatura: PositiveInt) -> Any:
        url = cls._get_url(
            endpoint=f"v2/integrations/omnichannel/invoices/{id_fatura}/payment-data"
        )
        headers = cls._get_headers()

        try:
            res = await cls.async_client.request(method="GET", url=url, headers=headers)
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"API request failed with status {e.response.status_code}"}
        except httpx.RequestError as e:
            return {"error": f"An error occurred while making the request: {str(e)}"}

    @classmethod
    async def aclose(cls) -> None:
        await cls.async_client.aclose()
