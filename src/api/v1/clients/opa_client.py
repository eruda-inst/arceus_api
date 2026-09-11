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

from .. import config, utils


class OpaClient:
    """Async client for the OPA API.

    OPA uses Bearer token authentication and a shared ``httpx.AsyncClient``.
    """

    # Base API URL from settings; endpoint paths are appended to it.
    _base_api_url: ClassVar[URL] = URL(config.settings.opa_base_api_url)

    # Secret token is unwrapped once at import time. Avoid logging this value.
    _access_token: ClassVar[str] = config.settings.opa_access_token.get_secret_value()

    # Per-phase timeout: connect, read, write and pool checkout.
    _timeout: ClassVar[Timeout] = Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)

    # Retry transient transport errors up to 3 times.
    _transport: ClassVar[AsyncHTTPTransport] = AsyncHTTPTransport(retries=3)

    # Shared async HTTP client. Reusing it keeps the connection pool warm.
    _async_client: ClassVar[AsyncClient] = AsyncClient(
        timeout=_timeout, transport=_transport
    )

    # Default headers shared by every request, including Bearer auth.
    _headers: ClassVar[Headers] = Headers(
        {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_access_token}",
        }
    )

    @classmethod
    async def _make_request(
        cls,
        endpoint: str,
        method: utils.HttpMethod = utils.HttpMethod.GET,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send an HTTP request to OPA and return the decoded JSON body.

        Args:
            endpoint: API path appended to the base URL.
            method: HTTP method; defaults to GET.
            payload: Optional JSON-serializable request body.

        Returns:
            The parsed JSON response as a dictionary.

        Raises:
            HTTPError: If the request fails or returns an error status.
            InvalidURL: If the constructed URL is invalid.
            CookieConflict: If httpx detects conflicting cookies.
            StreamError: If the response stream fails.
        """
        try:
            # Build the full endpoint URL from the configured base URL.
            url = URL(f"{cls._base_api_url}/{endpoint}")

            # Execute the request with shared timeout/transport/client settings.
            res = await cls._async_client.request(
                method=method, url=url, headers=cls._headers, json=payload
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
    async def get(
        cls, endpoint: str, filter: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """GET an OPA endpoint with an optional filter.

        OPA expects the filter as a JSON body under the ``filter`` key.
        """
        return await cls._make_request(endpoint=endpoint, payload={"filter": filter})
