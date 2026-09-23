"""
Client for interacting with the IXC ACS API.

Provides an asynchronous HTTP client with OAuth2 authentication and
automatic token refresh.
"""

import datetime as dt
from http import HTTPMethod
from typing import Any, ClassVar
from zoneinfo import ZoneInfo

from httpx2 import (
    URL,
    AsyncClient,
    AsyncHTTPTransport,
    CookieConflict,
    Headers,
    HTTPError,
    InvalidURL,
    QueryParams,
    StreamError,
    Timeout,
)

from .. import config


class IxcAcsClient:
    """
    Async HTTP client for the IXC ACS API.

    Handles OAuth2 authentication, token caching, and automatic refresh
    before each request.
    """

    _base_api_url: ClassVar[URL] = URL(config.settings.ixc_acs_base_api_url)
    _timeout: ClassVar[Timeout] = Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)
    _transport: ClassVar[AsyncHTTPTransport] = AsyncHTTPTransport(retries=3)
    _async_client: ClassVar[AsyncClient] = AsyncClient(
        timeout=_timeout, transport=_transport
    )
    _headers: ClassVar[Headers] = Headers({"Content-Type": "application/json"})
    _auth: ClassVar[dict[str, Any] | None] = None
    _tz: ClassVar[ZoneInfo] = ZoneInfo(config.settings.timezone)

    @classmethod
    async def _post_auth(cls) -> dict[str, Any]:
        """
        Request a new OAuth2 token from the IXC ACS token endpoint.

        Returns:
            The JSON response containing the access token and expiry.
        """
        auth_url = URL(f"{cls._base_api_url}/token/oauth")

        payload = {
            "client_id": config.settings.ixc_acs_client_id,
            "client_secret": config.settings.ixc_acs_client_secret.get_secret_value(),
        }

        res = await cls._async_client.post(
            url=auth_url, headers=cls._headers, json=payload
        )
        res.raise_for_status()
        return res.json()

    @classmethod
    async def _make_request(
        cls,
        endpoint: str,
        method: HTTPMethod = HTTPMethod.GET,
        payload: dict[str, Any] | None = None,
        query_params: QueryParams | None = None,
    ) -> dict[str, Any]:
        """
        Send an authenticated request to an IXC ACS API endpoint.

        Automatically obtains or refreshes the OAuth2 token if needed.

        Args:
            endpoint: API endpoint path (relative to base URL).
            method: HTTP method to use.
            payload: JSON body for the request.
            query_params: Query parameters.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            HTTPError: For HTTP-related errors.
            InvalidURL: If the URL is invalid.
            CookieConflict: If a cookie conflict occurs.
            StreamError: For stream-related errors.
        """
        # If no token exists, obtain one
        if cls._auth is None:
            cls._auth = await cls._post_auth()
        else:
            # Check if the token is about to expire (1 minute buffer)
            expires_at = dt.datetime.fromisoformat(cls._auth["expires_at"])
            expires_at += dt.timedelta(minutes=-1)
            expires_at = expires_at.astimezone(tz=cls._tz)
            now = dt.datetime.now(tz=cls._tz)

            if now >= expires_at:
                cls._auth = await cls._post_auth()

        try:
            # Attach the bearer token to the headers
            cls._headers["Authorization"] = f"Bearer {cls._auth['access_token']}"
            url = URL(f"{cls._base_api_url}/{endpoint}")

            res = await cls._async_client.request(
                method=method,
                url=url,
                headers=cls._headers,
                json=payload,
                params=query_params,
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
    async def get(cls, endpoint: str, query_params: QueryParams | None = None) -> Any:
        """
        Send a GET request to the IXC ACS API.

        Args:
            endpoint: API endpoint path.
            query_params: Optional query parameters.

        Returns:
            Parsed JSON response.
        """
        return await cls._make_request(endpoint=endpoint, query_params=query_params)

    @classmethod
    async def patch(cls, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Send a PATCH request to the IXC ACS API.

        Args:
            endpoint: API endpoint path.
            payload: JSON body for the request.

        Returns:
            Parsed JSON response.
        """
        return await cls._make_request(
            endpoint=endpoint, payload=payload, method=HTTPMethod.PATCH
        )

    @classmethod
    async def post(cls, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Send a POST request to the IXC ACS API.

        Args:
            endpoint: API endpoint path.
            payload: JSON body for the request.

        Returns:
            Parsed JSON response.
        """
        return await cls._make_request(
            endpoint=endpoint, payload=payload, method=HTTPMethod.POST
        )
