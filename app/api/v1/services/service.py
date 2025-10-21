from .. import clients, utils
from typing import Self, Optional, Dict
from fastapi import HTTPException, status
from pydantic import ValidationError, PositiveInt


class Service:
    """
    Classe de serviço base que fornece funcionalidades compartilhadas.

    Esta classe inicializa o cliente OPA e fornece um método para traduzir
    o protocolo de atendimento do OPA para o ID do cliente no sistema IXC.
    """

    def __init__(self: Self) -> None:
        """
        Inicializa o serviço base e o cliente da API OPA.
        """
        self.opa_cliente = clients.OpaCliente()
        self.ixc_cliente = clients.IXCCliente()

    async def _buscar_por_protocolo(self, protocolo: str) -> Dict:
        """Busca ID do cliente via protocolo OPA."""
        # Busca ID do cliente no OPA
        id_cliente_opa_res = await self.opa_cliente.get_id_cliente_opa(
            protocolo=protocolo
        )

        if not id_cliente_opa_res.get("data"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado no OPA.",
            )

        id_cliente_opa = id_cliente_opa_res["data"][0]["id_cliente"]

        # Busca ID do cliente no IXC via OPA
        id_cliente_ixc_res = await self.opa_cliente.get_id_cliente_ixc(
            id_cliente_opa=id_cliente_opa
        )

        if not id_cliente_ixc_res.get("data"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado no IXC através do protocolo OPA.",
            )

        return id_cliente_ixc_res

    async def _buscar_por_cnpj_cpf(self, cnpj_cpf: str) -> Dict:
        """Busca ID do cliente diretamente no IXC via CPF/CNPJ."""
        id_cliente_ixc_res = await self.ixc_cliente.get_id_cliente_ixc(
            cnpj_cpf=cnpj_cpf
        )

        if not id_cliente_ixc_res.get("registros"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado no IXC através do CNPJ/CPF.",
            )

        return id_cliente_ixc_res

    def _extrair_id_cliente_ixc(self, resposta: Dict) -> PositiveInt:
        """Extrai o ID do cliente da resposta validando a estrutura."""
        try:
            data = resposta.get("data")
            registros = resposta.get("registros", None)
            id_cliente_ixc = data[0]["id"] if data else registros[0]["id"]
            if not id_cliente_ixc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado no IXC.",
                )
            return id_cliente_ixc
        except (KeyError, IndexError) as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Estrutura da resposta inválida: {e}",
            )

    async def get_id_cliente_ixc(
        self: Self, protocolo: Optional[str] = None, cnpj_cpf: Optional[str] = None
    ) -> PositiveInt:
        """
        Obtém o ID do cliente no IXC a partir do protocolo de atendimento do OPA ou CPF/CNPJ.

        Realiza um dos seguintes processos:
        1. Via protocolo: Busca o ID do cliente no OPA e depois no IXC
        2. Via CPF/CNPJ: Busca diretamente no IXC

        Args:
            protocolo: O número do protocolo de atendimento do OPA.
            cnpj_cpf: O CPF ou CNPJ do cliente.

        Returns:
            O ID do cliente no sistema IXC.

        Raises:
            HTTPException: Se o cliente não for encontrado em qualquer uma das etapas
                           ou se ocorrer um erro de comunicação ou validação.
        """
        try:

            cnpj_cpf_formatado = (
                utils.formatar_cnpj_cpf(cnpj_cpf=cnpj_cpf) if cnpj_cpf else None
            )

            if not protocolo and not cnpj_cpf_formatado:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Protocolo ou CPF/CNPJ devem ser fornecidos.",
                )

            id_cliente_ixc_res = None

            if protocolo:
                id_cliente_ixc_res = await self._buscar_por_protocolo(protocolo)
            elif cnpj_cpf_formatado:
                id_cliente_ixc_res = await self._buscar_por_cnpj_cpf(cnpj_cpf_formatado)

            return self._extrair_id_cliente_ixc(id_cliente_ixc_res)

        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Validação da resposta falhou: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )
