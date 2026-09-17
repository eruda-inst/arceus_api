"""
Client for the IXC API using Basic Authentication.

Provides an asynchronous HTTP client for making requests to IXC endpoints.
"""

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
    """
    Async HTTP client for the IXC API.

    Uses Basic Authentication with a pre-encoded token.
    """

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
        """
        Send an authenticated request to an IXC API endpoint.

        Args:
            endpoint: API endpoint path.
            method: HTTP method to use.
            payload: JSON body for the request.
            include_ixcsoft: If True, adds the 'ixcsoft: listar' header.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            HTTPError: For HTTP-related errors.
            InvalidURL: If the URL is invalid.
            CookieConflict: If a cookie conflict occurs.
            StreamError: For stream-related errors.
        """
        try:
            headers = cls._headers.copy()

            # Add the special header required for listing endpoints
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
        """Close the underlying HTTP client session."""
        await cls._async_client.aclose()

    @classmethod
    async def post(cls, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Send a POST request to the IXC API.

        Args:
            endpoint: API endpoint path.
            payload: JSON body for the request.

        Returns:
            Parsed JSON response.
        """
        return await cls._make_request(endpoint=endpoint, payload=payload)

    @classmethod
    async def put(cls, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Send a PUT request to the IXC API.

        Args:
            endpoint: API endpoint path.
            payload: JSON body for the request.

        Returns:
            Parsed JSON response.
        """
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
        """
        Send a GET request to the IXC API with pagination and filtering.

        Args:
            endpoint: API endpoint path.
            grid_param: List of filter parameters.
            pagina: Page number (1-based).
            itens_por_pagina: Number of items per page.
            sort_order: Sort order (ASC or DESC).

        Returns:
            Parsed JSON response.
        """
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
