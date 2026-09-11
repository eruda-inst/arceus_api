import json
from base64 import b64encode
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
from pydantic import NonNegativeInt, PositiveInt

from .. import config, utils


class IxcClient:
    """Async client for the IXC Soft API.

    All requests share one ``httpx.AsyncClient`` so the connection pool is reused.
    """

    # SecretStr is unwrapped once at import time. Avoid logging this value.
    _access_token: ClassVar[str] = config.settings.ixc_access_token.get_secret_value()

    # IXC expects HTTP Basic auth, so the raw token is Base64-encoded once.
    _access_token_encoded: ClassVar[str] = b64encode(
        _access_token.encode("utf-8")
    ).decode("utf-8")

    # Base API URL from settings; endpoint paths are appended to it.
    _base_api_url: ClassVar[URL] = URL(config.settings.ixc_base_api_url)

    # Default headers shared by every request.
    _headers: ClassVar[Headers] = Headers(
        {
            "Content-Type": "application/json",
            "Authorization": f"Basic {_access_token_encoded}",
        }
    )

    # Per-phase timeout: connect, read, write and pool checkout.
    _timeout: ClassVar[Timeout] = Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)

    # Retry transient transport errors up to 3 times.
    _transport: ClassVar[AsyncHTTPTransport] = AsyncHTTPTransport(retries=3)

    # Shared async HTTP client. Reusing it keeps the connection pool warm.
    _async_client: ClassVar[AsyncClient] = AsyncClient(
        timeout=_timeout, transport=_transport
    )

    @classmethod
    async def _make_request(
        cls,
        endpoint: str,
        method: utils.HttpMethod = utils.HttpMethod.POST,
        payload: dict[str, Any] | None = None,
        include_ixcsoft: bool = False,
    ) -> dict[str, Any]:
        """Send an HTTP request to IXC and return the decoded JSON body.

        Args:
            endpoint: API path appended to the base URL.
            method: HTTP method; IXC commonly uses POST/PUT.
            payload: Optional JSON-serializable request body.
            include_ixcsoft: Add the ``ixcsoft: listar`` header required by
                some IXC list endpoints.

        Returns:
            The parsed JSON response as a dictionary.

        Raises:
            HTTPError: If the request fails or returns an error status.
            InvalidURL: If the constructed URL is invalid.
            CookieConflict: If httpx detects conflicting cookies.
            StreamError: If the response stream fails.
        """
        try:
            headers = cls._headers

            if include_ixcsoft:
                # IXC list endpoints use this custom header to select list mode.
                headers["ixcsoft"] = "listar"

            # Build the full endpoint URL from the configured base URL.
            url = URL(f"{cls._base_api_url}/{endpoint}")

            # Execute the request with shared timeout/transport/client settings.
            res = await cls._async_client.request(
                method=method, url=url, headers=headers, json=payload
            )

            # Raise for 4xx/5xx responses before trying to decode JSON.
            res.raise_for_status()
            return res.json()

        except HTTPError as exc:
            # Re-raise httpx HTTP errors with a consistent prefix.
            raise HTTPError(message=f"HTTPError: {exc}")
        except InvalidURL as exc:
            # Re-raise URL construction/parsing errors with context.
            raise InvalidURL(message=f"InvalidURL: {exc}")
        except CookieConflict as exc:
            # Re-raise cookie conflicts with context.
            raise CookieConflict(message=f"CookieConflict: {exc}")
        except StreamError as exc:
            # Re-raise response stream errors with context.
            raise StreamError(message=f"StreamError: {exc}")

    @classmethod
    async def post(cls, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Create/send data to an IXC endpoint using POST."""
        return await cls._make_request(endpoint=endpoint, payload=payload)

    @classmethod
    async def put(
        cls,
        endpoint: str,
        # IDs are NonNegativeInt because IXC may return 0 for some records,
        # and PositiveInt would reject those values.
        id: NonNegativeInt,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an IXC resource by ID using PUT."""
        return await cls._make_request(
            endpoint=f"{endpoint}/{id}", payload=payload, method=utils.HttpMethod.PUT
        )

    @classmethod
    async def get(
        cls,
        endpoint: str,
        grid_param: list[utils.Param],
        pagina: PositiveInt = 1,
        itens_por_pagina: PositiveInt = 10,
        sort_order: utils.SortOrder = utils.SortOrder.ASC,
    ) -> dict[str, Any]:
        """List IXC records using the grid/list convention.

        Args:
            endpoint: List endpoint path.
            grid_param: Pydantic filter models converted to IXC grid params.
            pagina: Page number, 1-based.
            itens_por_pagina: Number of records per page.
            sort_order: Sort direction.
        """
        # Convert Pydantic filter models into plain dictionaries for IXC.
        grid_param_dict = [gp.model_dump() for gp in grid_param]

        payload = {
            # IXC expects grid parameters as a JSON string inside the JSON body.
            "grid_param": json.dumps(grid_param_dict),
            "page": str(pagina),
            # "rp" means records per page in IXC's grid convention.
            "rp": str(itens_por_pagina),
            "sortorder": str(sort_order),
        }

        return await cls._make_request(
            endpoint=endpoint, payload=payload, include_ixcsoft=True
        )
