import httpx
from app.api.v1 import cores
from typing import Self, Any
from pydantic import PositiveInt


class FinanceiroAZ7Cliente:
    def __init__(self: Self) -> None:
        self.base_url = cores.settings.BASE_URL_7AZ
        self.api_key = cores.settings.API_KEY_7AZ
        self.timeout = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)
        self.async_client = httpx.AsyncClient(timeout=self.timeout)

    def _get_headers(self: Self) -> Any:
        return {"X-API-Key": self.api_key}

    def _get_url(self: Self, endpoint: str) -> str:
        return f"{self.base_url}/{endpoint}"

    async def get_chave_pix(self: Self, id_fatura: PositiveInt) -> Any:
        url = self._get_url(
            endpoint=f"v2/integrations/omnichannel/invoices/{id_fatura}/payment-data"
        )
        headers = self._get_headers()

        try:
            res = await self.async_client.request(
                method="GET", url=url, headers=headers
            )
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"API request failed with status {e.response.status_code}"}
        except httpx.RequestError as e:
            return {"error": f"An error occurred while making the request: {str(e)}"}

    async def aclose(self) -> None:
        await self.async_client.aclose()
