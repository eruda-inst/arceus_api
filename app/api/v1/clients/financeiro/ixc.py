import json
from .. import SortOrder, ixc
from app.api.v1 import schemas
from pydantic import PositiveInt
from typing import Dict, Self, Optional


class FinanceiroIXCCliente(ixc.IXCCliente):
    """Cliente IXC para operações financeiras."""

    async def get_contrato(self: Self, id_contrato: PositiveInt) -> Dict:
        """
        Busca um contrato específico no IXC pelo ID.

        Args:
            id_contrato (PositiveInt): O ID do contrato a ser buscado.

        Returns:
            Dict: A resposta da API IXC contendo os dados do contrato.
        """
        grid_param = [{"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="cliente_contrato", payload=payload)
        return data

    async def get_faturas_abertas(
        self: Self,
        id_cliente: PositiveInt,
        page: Optional[PositiveInt] = 1,
        per_page: Optional[PositiveInt] = 15,
        sortname: Optional[str] = "fn_areceber.id",
        sortorder: Optional[SortOrder] = SortOrder.ASC,
    ) -> Dict:
        """
        Busca faturas com status 'Aberto' de um cliente, com paginação.

        Args:
            id_cliente (PositiveInt): O ID do cliente.
            page (Optional[PositiveInt]): O número da página para a paginação.
            per_page (Optional[PositiveInt]): A quantidade de registros por página.
            sortname (Optional[str]): O campo para ordenação.
            sortorder (Optional[SortOrder]): A ordem de ordenação (ASC/DESC).

        Returns:
            Dict: A resposta da API IXC contendo a lista de faturas abertas.
        """
        grid_param = [
            {"TB": "fn_areceber.id_cliente", "OP": "=", "P": str(id_cliente)},
            {"TB": "fn_areceber.status", "OP": "=", "P": "A"},
        ]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await self._make_request(endpoint="fn_areceber", payload=payload)
        return data

    async def post_desbloqueio_em_confianca(
        self: Self, id_contrato: PositiveInt
    ) -> Dict:
        """
        Solicita o desbloqueio em confiança para um contrato.

        Args:
            id_contrato (PositiveInt): O ID do contrato a ser desbloqueado.

        Returns:
            Dict: A resposta da API IXC após a solicitação.
        """
        payload = {"id": id_contrato}
        data = await self._make_request(
            endpoint="desbloqueio_confianca", payload=payload, include_ixcsoft=False
        )
        return data

    async def get_linha_digitavel(self: Self, id_fatura: PositiveInt) -> Dict:
        """
        Busca a linha digitável de uma fatura específica.

        Args:
            id_fatura (PositiveInt): O ID da fatura.

        Returns:
            Dict: A resposta da API IXC contendo os dados da fatura.
        """
        grid_param = [{"TB": "fn_areceber.id", "OP": "=", "P": str(id_fatura)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="fn_areceber", payload=payload)
        return data

    async def get_credenciais(self: Self, id_cliente: PositiveInt) -> Dict:
        """
        Busca as credenciais de um cliente.

        Args:
            id_cliente (PositiveInt): O ID do cliente.

        Returns:
            Dict: A resposta da API IXC contendo os dados do cliente.
        """
        grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id_cliente)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="cliente", payload=payload)
        return data

    async def put_clientes(
        self: Self, id_cliente: PositiveInt, cliente: schemas.ClienteUpdate
    ) -> Dict:
        """
        Atualiza os dados de um cliente no IXC.

        Args:
            id_cliente (PositiveInt): O ID do cliente a ser atualizado.
            cliente (schemas.ClienteUpdate): Os dados do cliente para atualização.

        Returns:
            Dict: A resposta da API IXC após a tentativa de atualização.
        """
        data = await self._make_request(
            endpoint=f"cliente/{id_cliente}",
            payload=cliente,
            include_ixcsoft=False,
            method="PUT",
        )
        return data

    async def get_ultima_fatura_paga(self: Self, id_contrato: PositiveInt) -> Dict:
        """
        Busca a última fatura paga de um contrato específico.

        Filtra faturas com status 'Recebido' e ordena de forma descendente
        pelo ID para obter a mais recente.

        Args:
            id_contrato (PositiveInt): O ID do contrato.

        Returns:
            Dict: A resposta da API IXC contendo os dados da última fatura paga.
        """
        grid_param = [
            {"TB": "fn_areceber.id_contrato", "OP": "=", "P": str(id_contrato)},
            {"TB": "fn_areceber.status", "OP": "=", "P": "R"},
        ]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
            "sortname": "fn_areceber.id",
            "sortorder": "DESC",
        }
        data = await self._make_request(endpoint="fn_areceber", payload=payload)
        return data
