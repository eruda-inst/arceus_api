import json
from .. import ixc
from pydantic import PositiveInt
from app.api.v1 import schemas, utils
from typing import Dict, Self, Optional


class ComercialIXCCliente(ixc.IXCCliente):
    """Cliente para interações comerciais com a API do IXC."""

    async def get_status_acesso(self: Self, id_contrato: int) -> Dict:
        """
        Busca o status de acesso de um contrato de cliente no IXC.

        Args:
            id_contrato (int): O ID do contrato do cliente.

        Returns:
            Dict: A resposta da API IXC contendo os dados do contrato.
        """
        grid_param = [{"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="cliente_contrato", payload=payload)
        return data

    async def get_contratos(
        self: Self,
        id_cliente: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "cliente_contrato.id",
        sortorder: Optional[utils.SortOrder] = utils.SortOrder.ASC,
    ) -> Dict:
        """
        Busca os contratos de um cliente específico no IXC com paginação.

        Args:
            id_cliente (int): O ID do cliente.
            page (Optional[int]): O número da página para a paginação.
            per_page (Optional[int]): A quantidade de registros por página.
            sortname (Optional[str]): O campo para ordenação.
            sortorder (Optional[utils.SortOrder]): A ordem de ordenação (ASC/DESC).

        Returns:
            Dict: A resposta da API IXC contendo a lista de contratos.
        """
        grid_param = [
            {"TB": "cliente_contrato.id_cliente", "OP": "=", "P": str(id_cliente)}
        ]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await self._make_request(endpoint="cliente_contrato", payload=payload)
        return data

    async def post_leads(self: Self, lead: schemas.LeadIn) -> Dict:
        """
        Cria um novo lead no sistema IXC.

        Args:
            lead (schemas.LeadIn): O objeto Pydantic com os dados do lead.

        Returns:
            Dict: A resposta da API IXC após a criação do lead.
        """
        payload = lead.model_dump()
        data = await self._make_request(
            endpoint="contato", payload=payload, include_ixcsoft=False
        )
        return data

    async def get_login(self: Self, id_cliente: PositiveInt):
        grid_param = [{"TB": "radusuarios.id_cliente", "OP": "=", "P": str(id_cliente)}]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
        }
        data = await self._make_request(endpoint="radusuarios", payload=payload)
        return data
