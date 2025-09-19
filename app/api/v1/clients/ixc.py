import httpx
import base64
from ..core import settings
from fastapi import HTTPException, status
from typing import Dict, Any, List, Union, Self, Optional


class Cliente:
    def __init__(
        self: Self,
    ) -> None:
        self.token = settings.IXC_TOKEN
        self.host = settings.IXC_HOST
        self.base_url = f"https://{self.host}/webservice/v1"
        self.auth_header = self._create_auth_header()

    def _create_auth_header(
        self: Self,
    ) -> str:
        token_encoded = base64.b64encode(self.token.encode("utf-8")).decode("utf-8")
        return f"Basic {token_encoded}"

    def _get_headers(
        self: Self,
        include_ixcsoft: Optional[bool] = True,
    ) -> Dict[str, str]:
        headers = {"Authorization": self.auth_header}
        if include_ixcsoft:
            headers["ixcsoft"] = "listar"
        return headers

    async def _make_request(
        self: Self,
        endpoint: str,
        payload: Dict[str, Any],
        include_ixcsoft: Optional[bool] = True,
    ) -> Optional[Union[List[Dict[str, Any]], Dict[str, Any]]]:
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers(
            include_ixcsoft=include_ixcsoft,
        )
        try:
            async with httpx.AsyncClient(
                timeout=30.0,
            ) as async_client:
                res = await async_client.request(
                    method="POST",
                    url=url,
                    headers=headers,
                    json=payload,
                )
                res.raise_for_status()
                return res.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Falha na comunicação com o serviço IXC: {e.response.text}"
            ) from e
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Erro retornado pelo IXC: {e.response.text}"
            ) from e
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resposta inválida do servidor IXC: {e}"
            ) from e