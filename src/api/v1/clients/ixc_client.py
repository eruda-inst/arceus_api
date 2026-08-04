import base64
import json
from typing import Any

import httpx
from fastapi import HTTPException, status
from pydantic import PositiveInt

from .. import cores, utils


class IxcCliente:
    _host = cores.settings.ixc_host
    _token = cores.settings.ixc_token.get_secret_value()
    _token_encoded = base64.b64encode(_token.encode("utf-8")).decode("utf-8")
    _client = httpx.AsyncClient(timeout=30.0)
    _url = "https://{}/webservice/v1/{}"  # host, endpoint

    @classmethod
    def _create_auth_header(cls) -> str:
        return f"Basic {cls._token_encoded}"

    @classmethod
    def _get_headers(cls, include_ixcsoft: bool = True) -> dict[str, str]:
        headers = {"Authorization": cls._create_auth_header()}
        if include_ixcsoft:
            headers["ixcsoft"] = "listar"
        return headers

    @classmethod
    async def _make_request(
        cls,
        endpoint: str,
        payload: dict[str, Any],
        method: utils.HttpMethod = utils.HttpMethod.POST,
        include_ixcsoft: bool = True,
    ) -> dict[str, Any]:
        try:
            res = await cls._client.request(
                method=method,
                url=cls._url.format(cls._host, endpoint),
                headers=cls._get_headers(include_ixcsoft=include_ixcsoft),
                json=payload,
            )
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro do IXC: {e}",
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Falha na comunicação com o IXC: {e}",
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resposta inválida do IXC: {e}",
            )

    @classmethod
    async def post(cls, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        return await cls._make_request(
            endpoint=endpoint, payload=payload, include_ixcsoft=False
        )

    @classmethod
    async def put(
        cls, endpoint: str, id: PositiveInt, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return await cls._make_request(
            endpoint=f"{endpoint}/{id}",
            payload=payload,
            include_ixcsoft=False,
            method=utils.HttpMethod.PUT,
        )

    @classmethod
    async def get(
        cls,
        endpoint: str,
        grid_param: list[utils.Param],
        pagina: PositiveInt | None = 1,
        itens_por_pagina: PositiveInt | None = 10,
        sort_order: utils.SortOrder | None = utils.SortOrder.ASC,
    ) -> dict[str, Any]:
        grid_param_dict = [gp.model_dump() for gp in grid_param]
        payload = {
            "grid_param": json.dumps(grid_param_dict),
            "page": str(pagina),
            "rp": str(itens_por_pagina),
            "sortorder": str(sort_order),
        }
        return await cls._make_request(endpoint=endpoint, payload=payload)
