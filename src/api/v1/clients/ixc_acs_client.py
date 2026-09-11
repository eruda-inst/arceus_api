from datetime import datetime
from typing import Any, ClassVar
from zoneinfo import ZoneInfo

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


class IxcAcsClient:
    """Client for interacting with the IXC ACS API."""

    # Base URL used for all API requests.
    _base_api_url: ClassVar[URL] = URL(config.settings.ixc_acs_base_api_url)

    # Timeout configuration applied to the shared HTTP client.
    _timeout: ClassVar[Timeout] = Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)

    # Transport with automatic retries for transient network failures.
    _transport: ClassVar[AsyncHTTPTransport] = AsyncHTTPTransport(retries=3)

    # Shared AsyncClient instance. Reusing it enables connection pooling.
    _async_client: ClassVar[AsyncClient] = AsyncClient(
        timeout=_timeout, transport=_transport
    )

    # Default headers sent with every request.
    _headers: ClassVar[Headers] = Headers({"Content-Type": "application/json"})

    # Cached OAuth token payload. None until the first authentication.
    _auth: ClassVar[dict[str, Any] | None] = None

    @classmethod
    async def _post_auth(cls) -> dict[str, Any]:
        """Request a new OAuth token from the IXC ACS API."""
        auth_url = URL(f"{cls._base_api_url}/token/oauth")

        payload = {
            "client_id": config.settings.ixc_acs_client_id,
            "client_secret": config.settings.ixc_acs_client_secret.get_secret_value(),
        }

        # Send credentials and raise for non-2xx responses.
        res = await cls._async_client.post(
            url=auth_url, headers=cls._headers, json=payload
        )
        res.raise_for_status()
        return res.json()

    @classmethod
    async def _make_request(
        cls,
        endpoint: str,
        method: utils.HttpMethod = utils.HttpMethod.GET,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Send an authenticated request to an API endpoint.

        Fetches an OAuth token if none is cached, or refreshes it when expired.
        """
        # Authenticate on first use.
        if cls._auth is None:
            cls._auth = await cls._post_auth()
        else:
            # Parse token expiration and compare it in the API's expected timezone.
            datetime_ = datetime.fromisoformat(str(cls._auth["expires_at"]))

            expires_at = datetime_.astimezone(tz=ZoneInfo("America/Bahia"))
            now = datetime.now(tz=ZoneInfo("America/Bahia"))

            # Refresh the token if it has expired.
            if now >= expires_at:
                cls._auth = await cls._post_auth()

        try:
            # Attach the current bearer token and perform the request.
            cls._headers["Authorization"] = f"Bearer {cls._auth['access_token']}"
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
    async def get(cls, endpoint: str) -> dict[str, Any]:
        """Perform an authenticated GET request to the given endpoint."""
        return await cls._make_request(endpoint=endpoint)
