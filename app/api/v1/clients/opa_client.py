import httpx
from typing import Any
from .. import cores, utils
from fastapi import HTTPException, status


class OpaCliente:
    token = cores.settings.opa_token.get_secret_value()
    host = cores.settings.opa_host
    base_url = f"https://{host}/api/v1"
    headers = {"Authorization": f"Bearer {token}"}

    @classmethod
    async def _make_request(cls, endpoint: str, payload: Any) -> Any:
        url = f"{cls.base_url}/{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as async_client:
                res = await async_client.request(
                    method=utils.HttpMethod.GET,
                    url=url,
                    headers=cls.headers,
                    json=payload,
                )
                res.raise_for_status()
                return res.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro na API do OPA: {e}",
            )

    @classmethod
    async def get(
        cls,
        endpoint: str,
        filter: dict[str, Any],
        options: dict[str, Any] | None = None,
    ) -> Any:
        payload: dict[str, Any] = {"filter": filter, "options": options}
        data = await cls._make_request(endpoint=endpoint, payload=payload)
        return data
