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
    _base_api_url: ClassVar[str] = config.settings.ixc_acs_base_api_url
    _timeout: ClassVar[Timeout] = Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)
    _transport: ClassVar[AsyncHTTPTransport] = AsyncHTTPTransport(retries=3)
    _async_client: ClassVar[AsyncClient] = AsyncClient(
        timeout=_timeout, transport=_transport
    )
    _headers: ClassVar[Headers] = Headers({"Content-Type": "application/json"})
    _auth: ClassVar[dict[str, str | int] | None] = None

    @classmethod
    async def _post_auth(cls) -> dict[str, str | int]:
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
        method: utils.HttpMethod = utils.HttpMethod.GET,
        payload: Any = None,
    ) -> Any:
        if cls._auth is None:
            cls._auth = await cls._post_auth()
        else:
            datetime_ = datetime.fromisoformat(str(cls._auth["expires_at"]))

            expires_at = datetime_.astimezone(ZoneInfo("America/Bahia"))
            now = datetime.now(tz=ZoneInfo("America/Bahia"))

            if now >= expires_at:
                cls._auth = await cls._post_auth()

        try:
            cls._headers["Authorization"] = f"Bearer {cls._auth['access_token']}"
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
    async def get(cls, endpoint: str) -> dict[str, Any]:
        return await cls._make_request(endpoint=endpoint)
