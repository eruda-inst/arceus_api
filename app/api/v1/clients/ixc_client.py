import json
import httpx
import base64
from typing import Any
from .. import cores, utils
from pydantic import PositiveInt
from fastapi import HTTPException, status


class IXCCliente:
    token = cores.settings.IXC_TOKEN
    host = cores.settings.IXC_HOST
    base_url = f"https://{host}/webservice/v1"

    @classmethod
    def _create_auth_header(cls) -> str:
        token_encoded = base64.b64encode(cls.token.encode("utf-8")).decode("utf-8")
        return f"Basic {token_encoded}"

    @classmethod
    def _get_headers(cls, include_ixcsoft: bool = True) -> Any:
        headers = {"Authorization": cls._create_auth_header()}
        if include_ixcsoft:
            headers["ixcsoft"] = "listar"
        return headers

    @classmethod
    async def _make_request(
        cls,
        endpoint: str,
        payload: Any,
        method: str = "POST",
        include_ixcsoft: bool = True,
    ) -> Any:
        url = f"{cls.base_url}/{endpoint}"
        headers = cls._get_headers(include_ixcsoft=include_ixcsoft)

        try:
            async with httpx.AsyncClient(timeout=30.0) as async_client:
                res = await async_client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=payload,
                )
                res.raise_for_status()
                return res.json()

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro retornado pelo IXC: {e.response.text}",
            ) from e
        except httpx.RequestError as e:
            detail = f"Falha na comunicação com o serviço IXC: {str(e)}"

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=detail,
            ) from e
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resposta inválida do servidor IXC: {e}",
            ) from e

    @classmethod
    async def get_id_cliente_ixc(cls, cnpj_cpf: str) -> Any:
        grid_param = [{"TB": "cliente.cnpj_cpf", "OP": "=", "P": str(cnpj_cpf)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await cls._make_request(endpoint="cliente", payload=payload)
        return data

    @classmethod
    async def get_cliente_ixc(cls, id: PositiveInt) -> Any:
        grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await cls._make_request(endpoint="cliente", payload=payload)
        return data

    @classmethod
    async def post(cls, endpoint: str, payload: dict[str, Any]) -> Any:
        data = await cls._make_request(
            endpoint=endpoint, payload=payload, include_ixcsoft=False
        )
        return data

    @classmethod
    async def put(cls, endpoint: str, id: PositiveInt, payload: dict[str, Any]) -> Any:
        data = await cls._make_request(
            endpoint=f"{endpoint}/{id}",
            payload=payload,
            include_ixcsoft=False,
            method="PUT",
        )
        return data

    @classmethod
    async def get(
        cls,
        endpoint: str,
        grid_param: list[dict[str, str]],
        pagina: PositiveInt | None = 1,
        itens_por_pagina: PositiveInt | None = 10,
        sort_order: utils.SortOrder | None = utils.SortOrder.ASC,
    ) -> Any:
        payload = {
            "grid_param": json.dumps(obj=grid_param),
            "page": str(pagina),
            "rp": str(itens_por_pagina),
            "sortorder": str(sort_order),
        }
        data = await cls._make_request(endpoint=endpoint, payload=payload)
        return data
