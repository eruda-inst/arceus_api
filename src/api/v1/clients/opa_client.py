"""
Client for the OPA API using Bearer token authentication.

Provides an asynchronous HTTP client for making requests to OPA endpoints.
"""

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
    """
    Async HTTP client for the OPA API.

    Uses a Bearer token for authentication.
    """

    _base_api_url: ClassVar[URL] = URL(config.settings.opa_base_api_url)
    _access_token: ClassVar[str] = config.settings.opa_access_token.get_secret_value()
    _timeout: ClassVar[Timeout] = Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)
    _transport: ClassVar[AsyncHTTPTransport] = AsyncHTTPTransport(retries=3)
    _async_client: ClassVar[AsyncClient] = AsyncClient(
        timeout=_timeout, transport=_transport
    )
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
        """
        Send an authenticated request to an OPA API endpoint.

        Args:
            endpoint: API endpoint path.
            method: HTTP method to use.
            payload: JSON body for the request.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            HTTPError: For HTTP-related errors.
            InvalidURL: If the URL is invalid.
            CookieConflict: If a cookie conflict occurs.
            StreamError: For stream-related errors.
        """
        try:
            url = URL(f"{cls._base_api_url}/{endpoint}")
            res = await cls._async_client.request(
                method=method, url=url, headers=cls._headers, json=payload
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
    async def get(
        cls, endpoint: str, filter: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Send a GET request to the OPA API.

        Args:
            endpoint: API endpoint path.
            filter: Optional filter dictionary to include in the payload.

        Returns:
            Parsed JSON response.
        """
        return await cls._make_request(endpoint=endpoint, payload={"filter": filter})
