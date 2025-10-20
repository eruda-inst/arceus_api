import json
import httpx
import base64
from .. import core
from typing import Dict, Self
from pydantic import PositiveInt
from fastapi import HTTPException, status


class IXCCliente:
    """
    Cliente base para interagir com a API do IXC Provedor.

    Esta classe abstrata lida com a autenticação, montagem de requisições
    e tratamento de erros comuns ao se comunicar com a API do IXC. As classes
    filhas devem implementar os métodos específicos para cada endpoint.
    """

    def __init__(self: Self) -> None:
        """
        Inicializa o cliente base para a API do IXC Provedor.

        Configura o token, host, URL base e o cabeçalho de autenticação
        a partir das configurações do ambiente.
        """
        self.token = core.settings.IXC_TOKEN
        self.host = core.settings.IXC_HOST
        self.base_url = f"https://{self.host}/webservice/v1"
        self.auth_header = self._create_auth_header()

    def _create_auth_header(self: Self) -> str:
        """
        Cria o cabeçalho de autenticação Basic a partir do token.

        O token é codificado em Base64, conforme exigido pela API do IXC.

        Returns:
            str: O cabeçalho de autorização no formato "Basic <token_encoded>".
        """
        token_encoded = base64.b64encode(self.token.encode("utf-8")).decode("utf-8")
        return f"Basic {token_encoded}"

    def _get_headers(self: Self, include_ixcsoft: bool = True) -> Dict:
        """
        Monta os cabeçalhos para a requisição à API IXC.

        Args:
            include_ixcsoft (bool): Se True, inclui o cabeçalho "ixcsoft: listar",
                                    usado para consultas de listagem.

        Returns:
            Dict: Um dicionário contendo os cabeçalhos da requisição.
        """
        headers = {"Authorization": self.auth_header}
        if include_ixcsoft:
            headers["ixcsoft"] = "listar"
        return headers

    async def _make_request(
        self: Self,
        endpoint: str,
        payload: Dict,
        method: str = "POST",
        include_ixcsoft: bool = True,
    ) -> Dict:
        """
        Realiza uma requisição assíncrona para um endpoint da API IXC.

        Este método encapsula a lógica de requisição, incluindo a montagem
        da URL, cabeçalhos e tratamento de erros comuns, convertendo exceções
        de HTTP e de rede em `HTTPException` do FastAPI.

        Args:
            endpoint (str): O endpoint da API para o qual a requisição será feita.
            payload (Dict): O corpo da requisição a ser enviado como JSON.
            method (str): O método HTTP a ser utilizado (e.g., "POST", "PUT").
            include_ixcsoft (bool): Se True, inclui o cabeçalho "ixcsoft: listar".

        Returns:
            Dict: A resposta da API em formato de dicionário.

        Raises:
            HTTPException: Em caso de erros de status HTTP, falhas de comunicação
                           ou se a resposta não for um JSON válido.
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers(include_ixcsoft=include_ixcsoft)

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
            if hasattr(e, "response") and e.response is not None:
                detail = f"Falha na comunicação com o serviço IXC: {e.response.text}"

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=detail,
            ) from e
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Resposta inválida do servidor IXC: {e}",
            ) from e

    async def get_valor_e_data_vencimento(self: Self, id_contrato: int) -> Dict:
        """
        Busca o valor e a data de vencimento de faturas de um contrato.

        Args:
            id_contrato (int): O ID do contrato.

        Returns:
            Dict: A resposta da API IXC contendo os dados das faturas.
        """
        grid_param = [
            {"TB": "fn_areceber.id_contrato", "OP": "=", "P": str(id_contrato)}
        ]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="fn_areceber", payload=payload)
        return data

    async def get_id_cliente_ixc(self: Self, cnpj_cpf: str) -> Dict:
        """
        Obtém o ID do cliente no IXC a partir do CPF ou CNPJ.

        Args:
            cnpj_cpf (str): O CPF ou CNPJ do cliente.

        Returns:
            PositiveInt: O ID do cliente no IXC.
        """
        grid_param = [{"TB": "cliente.cnpj_cpf", "OP": "=", "P": str(cnpj_cpf)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="cliente", payload=payload)
        return data
