from typing import Any

import httpx
from fastapi import HTTPException, status

from .. import cores, utils


class OpaCliente:
    _host = cores.settings.opa_host
    _token = cores.settings.opa_token.get_secret_value()
    _headers = {"Authorization": f"Bearer {_token}"}
    _url = "https://{}/api/v1/{}"  # host, endpoint
    _client = httpx.AsyncClient(timeout=30.0)

    @classmethod
    async def _make_request(cls, endpoint: str, payload: Any) -> dict[str, Any]:
        try:
            res = await cls._client.request(
                method=utils.HttpMethod.GET,
                url=cls._url.format(cls._host, endpoint),
                headers=cls._headers,
                json=payload,
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
