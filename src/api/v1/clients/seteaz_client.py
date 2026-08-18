from typing import Any, ClassVar

from httpx import URL, Headers

from ..config_core import settings
from .httpx_client import HttpxClient


class SevenAZClient(HttpxClient):
    _headers: ClassVar[Headers] = Headers(
        {"X-API-Key": settings.api_key_7az.get_secret_value()}
    )
    _base_url: ClassVar[str] = settings.base_api_url_7az

    @classmethod
    async def get(cls, endpoint: str) -> Any:
        url = URL(f"{cls._base_url}/{endpoint}")
        return await cls._make_request(url=url, headers=cls._headers)
