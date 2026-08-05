from typing import Any

import httpx
from fastapi import HTTPException, status

from .. import cores, utils


class OpaCliente:
    @staticmethod
    async def _make_request(endpoint: str, payload: Any) -> dict[str, Any]:
        try:
            host = cores.settings.opa_host
            token = cores.settings.opa_token.get_secret_value()
            headers = {"Authorization": f"Bearer {token}"}
            url = f"https://{host}/api/v1/{endpoint}"
            client = httpx.AsyncClient(timeout=30.0)

            res = await client.request(
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
