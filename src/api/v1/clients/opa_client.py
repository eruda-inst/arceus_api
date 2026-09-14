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

from .. import config


class OpaClient:
    """Client for interacting with the OPA API."""

    # Base URL used for all API requests.
    _base_api_url: ClassVar[URL] = URL(config.settings.opa_base_api_url)

    # API access token loaded from settings.
    _access_token: ClassVar[str] = config.settings.opa_access_token.get_secret_value()

    # Timeout configuration applied to the shared HTTP client.
    _timeout: ClassVar[Timeout] = Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)

    # Transport with automatic retries for transient network failures.
    _transport: ClassVar[AsyncHTTPTransport] = AsyncHTTPTransport(retries=3)

    # Shared AsyncClient instance. Reusing it enables connection pooling.
    _async_client: ClassVar[AsyncClient] = AsyncClient(
        timeout=_timeout, transport=_transport
    )

    # Default headers sent with every request, including bearer authentication.
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
        method: HTTPMethod = HTTPMethod.GET,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send an authenticated request to an API endpoint."""
        try:
            # Build the full endpoint URL and perform the request.
            url = URL(f"{cls._base_api_url}/{endpoint}")
            res = await cls._async_client.request(
                method=method, url=url, headers=cls._headers, json=payload
            )
            res.raise_for_status()
            return res.json()

        # Normalize low-level httpx errors with clearer context.
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
        """Close the shared AsyncClient and release resources."""
        await cls._async_client.aclose()

    @classmethod
    async def get(
        cls, endpoint: str, filter: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Perform an authenticated GET request with an optional filter payload."""
        return await cls._make_request(endpoint=endpoint, payload={"filter": filter})
