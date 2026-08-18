import base64
import json
from typing import ClassVar

from httpx import URL, Headers
from pydantic import PositiveInt

from .. import utils
from ..config_core import settings
from .httpx_client import HttpxClient


class IxcClient(HttpxClient):
    _token: ClassVar[str] = settings.ixc_token.get_secret_value()
    _token_encoded: ClassVar[str] = base64.b64encode(_token.encode("utf-8")).decode(
        "utf-8"
    )
    _base_url: ClassVar[str] = settings.base_api_url_ixc
    _headers: ClassVar[Headers] = Headers({"Authorization": f"Basic {_token_encoded}"})

    @classmethod
    def _include_ixcsoft(cls) -> Headers:
        return Headers({**cls._headers, "ixcsoft": "listar"})

    @classmethod
    async def post(
        cls, endpoint: str, payload: dict[str, str | int]
    ) -> dict[str, str | int]:
        url = URL(f"{cls._base_url}/{endpoint}")
        return await cls._make_request(
            url=url, payload=payload, method=utils.HttpMethod.POST, headers=cls._headers
        )

    @classmethod
    async def put(
        cls, endpoint: str, id: PositiveInt, payload: dict[str, str | int]
    ) -> dict[str, str | int]:
        url = URL(f"{cls._base_url}/{endpoint}/{id}")
        return await cls._make_request(
            url=url, payload=payload, method=utils.HttpMethod.PUT, headers=cls._headers
        )

    @classmethod
    async def get(
        cls,
        endpoint: str,
        grid_param: list[utils.Param],
        pagina: PositiveInt | None = 1,
        itens_por_pagina: PositiveInt | None = 10,
        sort_order: utils.SortOrder | None = utils.SortOrder.ASC,
    ) -> dict[str, str | int]:
        grid_param_dict = [gp.model_dump() for gp in grid_param]
        payload = {
            "grid_param": json.dumps(grid_param_dict),
            "page": str(pagina),
            "rp": str(itens_por_pagina),
            "sortorder": str(sort_order),
        }
        url = URL(f"{cls._base_url}/{endpoint}")
        headers = cls._include_ixcsoft()
        return await cls._make_request(
            url=url, payload=payload, method=utils.HttpMethod.POST, headers=headers
        )
