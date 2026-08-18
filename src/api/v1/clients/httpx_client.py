from typing import Any, ClassVar

from httpx import (
    URL,
    AsyncClient,
    CookieConflict,
    Headers,
    HTTPError,
    InvalidURL,
    StreamError,
    Timeout,
)

from .. import utils


class HttpxClient:
    _timeout: ClassVar[Timeout] = Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)
    _client: ClassVar[AsyncClient] = AsyncClient(timeout=_timeout)

    @classmethod
    async def _make_request(
        cls,
        url: URL,
        headers: Headers,
        method: utils.HttpMethod = utils.HttpMethod.GET,
        payload: Any = None,
    ) -> Any:
        try:
            res = await cls._client.request(
                method=method, url=url, headers=headers, json=payload
            )
            _ = res.raise_for_status()
            return res.json()
        except HTTPError as exc:
            raise HTTPError(message=f"HTTPError: {exc}")
        except InvalidURL as exc:
            raise InvalidURL(message=f"InvalidURL: {exc}")
        except CookieConflict as exc:
            raise CookieConflict(message=f"CookieConflict: {exc}")
        except StreamError as exc:
            raise StreamError(message=f"StreamError: {exc}")
