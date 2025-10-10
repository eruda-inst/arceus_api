import httpx
from app.api.v1 import core
from typing import Self, Dict
from pydantic import PositiveInt


class FinanceiroAZ7Cliente:
    """Cliente para interagir com a API financeira da 7AZ."""

    def __init__(self: Self) -> None:
        """
        Inicializa o cliente para a API financeira da 7AZ.

        Configura a URL base, a chave de API, os timeouts e o cliente HTTP assíncrono.
        """
        self.base_url = core.settings.BASE_URL_7AZ
        self.api_key = core.settings.API_KEY_7AZ
        self.timeout = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=1.0)
        self.async_client = httpx.AsyncClient(timeout=self.timeout)

    def _get_headers(self: Self) -> Dict:
        """
        Monta os cabeçalhos de autenticação para as requisições.

        Returns:
            Dict: Um dicionário com o cabeçalho X-API-Key.
        """
        return {"X-API-Key": self.api_key}

    def _get_url(self: Self, endpoint: str) -> str:
        """
        Constrói a URL completa para um endpoint da API.

        Args:
            endpoint (str): O endpoint específico da API.

        Returns:
            str: A URL completa para a requisição.
        """
        return f"{self.base_url}/{endpoint}"

    async def get_chave_pix(self: Self, id_fatura: PositiveInt) -> Dict:
        """
        Busca os dados de pagamento (chave PIX) para uma fatura específica.

        Args:
            id_fatura (PositiveInt): O ID da fatura para a qual os dados de pagamento são solicitados.

        Returns:
            Dict: Um dicionário com os dados de pagamento retornados pela API
                  ou uma mensagem de erro em caso de falha.
        """
        url = self._get_url(
            endpoint=f"v2/integrations/omnichannel/invoices/{id_fatura}/payment-data"
        )
        headers = self._get_headers()

        try:
            res = await self.async_client.request(
                method="GET", url=url, headers=headers
            )
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"API request failed with status {e.response.status_code}"}
        except httpx.RequestError as e:
            return {"error": f"An error occurred while making the request: {str(e)}"}

    async def aclose(self) -> None:
        """
        Fecha a sessão do cliente HTTP assíncrono.

        Deve ser chamado para liberar os recursos adequadamente.
        """
        await self.async_client.aclose()
