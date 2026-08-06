from typing import Any

import httpx
from fastapi import HTTPException, status

from .. import utils
from ..config_core import settings


class OpaCliente:
    _token = settings.opa_token.get_secret_value()
    _timeout = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)
    _client = httpx.AsyncClient(timeout=_timeout)
    _base_url = settings.base_api_url_opa

    @classmethod
    async def _make_request(cls, endpoint: str, payload: Any) -> dict[str, Any]:
        try:
            headers = {"Authorization": f"Bearer {cls._token}"}
            url = f"{cls._base_url}/{endpoint}"

            res = await cls._client.request(
                method=utils.HttpMethod.GET, url=url, headers=headers, json=payload
            )
            res.raise_for_status()

            return res.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro do OPA: {e}",
            )

    @classmethod
    async def get(
        cls,
        endpoint: str,
        filter: dict[str, Any],
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"filter": filter, "options": options}
        data = await cls._make_request(endpoint=endpoint, payload=payload)
        return data
