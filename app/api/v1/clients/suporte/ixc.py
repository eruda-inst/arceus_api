import json
from .. import ixc
from app.api.v1 import schemas, utils
from typing import Dict, Self, Optional


class SuporteIXCCliente(ixc.IXCCliente):
    """Cliente IXC para operações de suporte."""

    async def get_contratos(
        self: Self,
        id_cliente: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "cliente_contrato.id",
        sortorder: Optional[utils.SortOrder] = utils.SortOrder.ASC,
    ) -> Dict:
        """
        Busca os contratos ativos de um cliente no IXC, com paginação.

        Exclui contratos com status Inativo ('I'), Novo ('N') ou Desativado ('D').

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
            {"TB": "cliente_contrato.id_cliente", "OP": "=", "P": str(id_cliente)},
            {"TB": "cliente_contrato.status", "OP": "!=", "P": "I"},
            {"TB": "cliente_contrato.status", "OP": "!=", "P": "N"},
            {"TB": "cliente_contrato.status", "OP": "!=", "P": "D"},
        ]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await self._make_request("cliente_contrato", payload)
        return data

    async def get_status_conexao(self: Self, id_login: int) -> Dict:
        """
        Busca o status de conexão de um login de usuário.

        Args:
            id_login (int): O ID do login do usuário (radusuarios).

        Returns:
            Dict: A resposta da API IXC contendo os dados do usuário.
        """
        grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request("radusuarios", payload)
        return data

    async def get_status_onu(
        self: Self, id_login: Optional[int] = None, mac_onu: Optional[str] = None
    ) -> Dict:
        """
        Busca o status de uma ONU pelo ID do login ou pelo MAC address.

        Args:
            id_login (Optional[int]): O ID do login associado à ONU.
            mac_onu (Optional[str]): O MAC address da ONU.

        Returns:
            Dict: A resposta da API IXC contendo os dados da ONU.
        """
        query_field = "id_login" if id_login else "mac"
        query_value = id_login if id_login else mac_onu
        grid_param = [
            {
                "TB": f"radpop_radio_cliente_fibra.{query_field}",
                "OP": "=",
                "P": str(query_value),
            }
        ]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(
            endpoint="radpop_radio_cliente_fibra", payload=payload
        )
        return data

    async def post_atendimentos(self: Self, atendimento: schemas.AtendimentoIn) -> Dict:
        """
        Cria um novo ticket de suporte (atendimento).

        Args:
            atendimento (schemas.AtendimentoIn): Os dados do atendimento a ser criado.

        Returns:
            Dict: A resposta da API IXC após a criação do ticket.
        """
        payload = atendimento.model_dump()
        return await self._make_request(
            endpoint="su_ticket", payload=payload, include_ixcsoft=False
        )

    async def post_desconectar_cliente(self: Self, id_login: int) -> Dict:
        """
        Força a desconexão de um cliente conectado.

        Args:
            id_login (int): O ID do login do cliente a ser desconectado.

        Returns:
            Dict: A resposta da API IXC.
        """
        payload = {"id": id_login}
        data = await self._make_request(
            endpoint="desconectar_clientes", payload=payload, include_ixcsoft=False
        )
        return data

    async def get_atendimentos(
        self: Self,
        id_login: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "su_ticket.id",
        sortorder: Optional[utils.SortOrder] = utils.SortOrder.ASC,
    ) -> Dict:
        """
        Busca os atendimentos em aberto para um determinado login.

        Exclui atendimentos com status Solucionado ('S') ou Cancelado ('C').

        Args:
            id_login (int): O ID do login do cliente.
            page (Optional[int]): O número da página para a paginação.
            per_page (Optional[int]): A quantidade de registros por página.
            sortname (Optional[str]): O campo para ordenação.
            sortorder (Optional[utils.SortOrder]): A ordem de ordenação (ASC/DESC).

        Returns:
            Dict: A resposta da API IXC contendo a lista de atendimentos.
        """
        grid_param = [
            {"TB": "su_ticket.id_login", "OP": "=", "P": str(id_login)},
            {"TB": "su_ticket.su_status", "OP": "!=", "P": "S"},
            {"TB": "su_ticket.su_status", "OP": "!=", "P": "C"},
        ]
        payload = {
            "grid_param": json.dumps(obj=grid_param),
            "page": page,
            "rp": per_page,
            "sortname": sortname,
            "sortorder": sortorder,
        }
        data = await self._make_request(endpoint="su_ticket", payload=payload)
        return data

    async def get_id_login(self: Self, id_contrato: int) -> Dict:
        """
        Busca o ID do login (radusuarios) associado a um contrato.

        Args:
            id_contrato (int): O ID do contrato.

        Returns:
            Dict: A resposta da API IXC contendo os dados do login.
        """
        grid_param = [
            {"TB": "radusuarios.id_contrato", "OP": "=", "P": str(id_contrato)}
        ]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="radusuarios", payload=payload)
        return data

    async def get_onu_mac(self: Self, id_login: int) -> Dict:
        """
        Busca o MAC da ONU associado a um ID de login.

        Args:
            id_login (int): O ID do login do usuário.

        Returns:
            Dict: A resposta da API IXC contendo os dados do usuário.
        """
        grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="radusuarios", payload=payload)
        return data

    async def get_login(self: Self, id_login: int) -> Dict:
        """
        Busca os dados de um login pelo seu ID.

        Args:
            id_login (int): O ID do login (radusuarios).

        Returns:
            Dict: A resposta da API IXC contendo os dados do login.
        """
        grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
        payload = {"grid_param": json.dumps(obj=grid_param)}
        data = await self._make_request(endpoint="radusuarios", payload=payload)
        return data

    async def put_ip(self: Self, id_login: int, ip: schemas.IPUpdate) -> Dict:
        """
        Atualiza o endereço IP de um login de usuário.

        Args:
            id_login (int): O ID do login a ser atualizado.
            ip (schemas.IPUpdate): O objeto com os novos dados de IP.

        Returns:
            Dict: A resposta da API IXC após a tentativa de atualização.
        """
        data = await self._make_request(
            endpoint=f"radusuarios/{id_login}",
            payload=ip,
            include_ixcsoft=False,
            method="PUT",
        )
        return data

    async def post_limpar_mac(self: Self, id_login: int) -> Dict:
        """
        Executa a rotina de limpar MAC para um login de usuário.

        Args:
            id_login (int): O ID do login para o qual o MAC será limpo.

        Returns:
            Dict: A resposta da API IXC.
        """
        payload = {"get_id": id_login}
        data = await self._make_request(
            endpoint="radusuarios_25452", payload=payload, include_ixcsoft=False
        )
        return data
