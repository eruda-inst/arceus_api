from typing import Any, ClassVar

from httpx import URL, Headers

from ..config import settings
from .httpx_client import HttpxClient


class SevenAZClient(HttpxClient):
    _headers: ClassVar[Headers] = Headers(
        {"X-API-Key": settings.seven_az_api_key.get_secret_value()}
    )
    _base_url: ClassVar[str] = settings.seven_az_base_api_url

    @classmethod
    async def get(cls, endpoint: str) -> Any:
        url = URL(f"{cls._base_url}/{endpoint}")
        return await cls._make_request(url=url, headers=cls._headers)
