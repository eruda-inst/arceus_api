from typing import Any, ClassVar

from httpx import URL, Headers

from ..config import settings
from .httpx_client import HttpxClient


class OpaClient(HttpxClient):
    _token: ClassVar[str] = settings.opa_token.get_secret_value()
    _base_url: ClassVar[str] = settings.base_api_url_opa
    _headers: ClassVar[Headers] = Headers({"Authorization": f"Bearer {_token}"})

    @classmethod
    async def get(cls, endpoint: str, filter: dict[str, str | int]) -> Any:
        payload = {"filter": filter}
        url = URL(f"{cls._base_url}/{endpoint}")
        data = await cls._make_request(url=url, headers=cls._headers, payload=payload)
        return data
