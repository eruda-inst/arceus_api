import base64
import json
from http import HTTPMethod
from typing import Any, ClassVar

from httpx import (
    URL,
    AsyncClient,
    AsyncHTTPTransport,
    CookieConflict,
    Headers,
    HTTPError,
    InvalidURL,
    StreamError,
    Timeout,
)
from pydantic import PositiveInt

from .. import config, utils


class IxcClient:
    _timeout: ClassVar[Timeout] = Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)
    _transport: ClassVar[AsyncHTTPTransport] = AsyncHTTPTransport(retries=3)
    _async_client: ClassVar[AsyncClient] = AsyncClient(
        timeout=_timeout, transport=_transport
    )
    _token: ClassVar[str] = config.settings.ixc_access_token.get_secret_value()
    _token_encoded: ClassVar[str] = base64.b64encode(_token.encode("utf-8")).decode(
        "utf-8"
    )
    _base_api_url: ClassVar[str] = config.settings.ixc_base_api_url
    _headers: ClassVar[Headers] = Headers(
        {"Content-Type": "application/json", "Authorization": f"Basic {_token_encoded}"}
    )

    @classmethod
    async def _make_request(
        cls,
        endpoint: str,
        method: HTTPMethod = HTTPMethod.POST,
        payload: dict[str, Any] | None = None,
        include_ixcsoft: bool = False,
    ) -> dict[str, Any]:
        try:
            headers = cls._headers.copy()

            if include_ixcsoft:
                headers["ixcsoft"] = "listar"

            url = URL(f"{cls._base_api_url}/{endpoint}")

            res = await cls._async_client.request(
                method=method, url=url, headers=headers, json=payload
            )
            res.raise_for_status()
            return res.json()
        except HTTPError as exc:
            raise HTTPError(message=f"HTTPError: {exc}")
        except InvalidURL as exc:
            raise InvalidURL(message=f"InvalidURL: {exc}")
        except CookieConflict as exc:
            raise CookieConflict(message=f"CookieConflict: {exc}")
        except StreamError as exc:
            raise StreamError(message=f"StreamError: {exc}")

    @classmethod
    async def aclose(cls) -> None:
        "Close the shared AsyncClient and releases resources."
        await cls._async_client.aclose()

    @classmethod
    async def post(cls, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        return await cls._make_request(endpoint=endpoint, payload=payload)

    @classmethod
    async def put(cls, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        return await cls._make_request(
            endpoint=endpoint, payload=payload, method=HTTPMethod.PUT
        )

    @classmethod
    async def get(
        cls,
        endpoint: str,
        grid_param: list[utils.Param],
        pagina: PositiveInt | None = 1,
        itens_por_pagina: PositiveInt | None = 10,
        sort_order: utils.SortOrder | None = utils.SortOrder.ASC,
    ) -> Any:
        grid_param_dict = [gp.model_dump() for gp in grid_param]
        payload = {
            "grid_param": json.dumps(grid_param_dict),
            "page": str(pagina),
            "rp": str(itens_por_pagina),
            "sortorder": str(sort_order),
        }
        return await cls._make_request(
            endpoint=endpoint, payload=payload, include_ixcsoft=True
        )
