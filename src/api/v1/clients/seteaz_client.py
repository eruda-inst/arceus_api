from typing import Any

import httpx
from pydantic import PositiveInt

from ..config_core import settings


class SeteAZCliente:
    _base_url = settings.base_api_url_7az
    _api_key = settings.api_key_7az.get_secret_value()
    _timeout = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)
    _client = httpx.AsyncClient(timeout=_timeout)

    @classmethod
    def _get_headers(cls) -> Any:
        return {"X-API-Key": cls._api_key}

    @classmethod
    def _get_url(cls, endpoint: str) -> str:
        return f"{cls._base_url}/{endpoint}"

    @classmethod
    async def get_fatura(cls, id_fatura: PositiveInt) -> Any:
        url = cls._get_url(
            endpoint=f"v2/integrations/omnichannel/invoices/{id_fatura}/payment-data"
        )
        headers = cls._get_headers()
        res = await cls._client.request(method="GET", url=url, headers=headers)
        return res.json()

    @classmethod
    async def aclose(cls) -> None:
        await cls._client.aclose()
