from . import service
from typing import Self, Optional
from .. import schemas, clients, utils
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError, PositiveInt


class TriagemService(service.Service):
    """
    Serviço para encapsular a lógica de negócios relacionada à triagem de clientes.
    """

    def __init__(self: Self) -> None:
        """
        Inicializa o serviço de triagem e o cliente IXC correspondente.
        """
        super().__init__()
        self.triagem_ixc_cliente = clients.TriagemIXCCliente()

    async def get_contato_cliente(
        self: Self,
        protocolo: Optional[str] = None,
        cnpj_cpf: Optional[str] = None,
    ) -> schemas.ContatoOut:
        """
        Busca as informações de contato de um cliente.

        Args:
            protocolo: O protocolo de atendimento do cliente a ser buscado.
            cnpj_cpf: O CPF ou CNPJ do cliente a ser buscado.

        Returns:
            Os dados de contato do cliente.
        """
        try:
            id_cliente = await self.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            res = await self.triagem_ixc_cliente.get_clientes(id_cliente=id_cliente)
            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado.",
                )

            contato = res["registros"][0]["telefone_celular"]
            return schemas.ContatoOut(telefone_celular=contato)
        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Erro de validação: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {str(e)}",
            )

    async def put_contato_cliente(
        self: Self,
        contato: schemas.ContatoUpdate,
        protocolo: Optional[str] = None,
        cnpj_cpf: Optional[str] = None,
    ) -> schemas.MensagemOut:
        """
        Atualiza as informações de contato de um cliente.

        Args:
            protocolo: O protocolo de atendimento do cliente a ser atualizado.
            contato: Os novos dados de contato a serem aplicados.
            cnpj_cpf: O CPF ou CNPJ do cliente a ser atualizado.

        Returns:
            Uma mensagem de confirmação da atualização.

        Raises:
            HTTPException: Se o cliente não for encontrado ou ocorrer um erro.
        """
        try:
            id_cliente = await self.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            res = await self.triagem_ixc_cliente.get_clientes(id_cliente=id_cliente)
            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado.",
                )

            cliente_antigo = res["registros"][0]
            novo_contato = contato.model_dump()

            cliente_atualizado = {**cliente_antigo, **novo_contato}

            if "cep" in cliente_atualizado:
                cliente_atualizado["cep"] = utils.formatar_cep(
                    cep=cliente_atualizado["cep"]
                )

            del cliente_atualizado["id"]

            res = await self.triagem_ixc_cliente.put_clientes(
                id_cliente=id_cliente, cliente=cliente_atualizado
            )

            mensagem = "Nenhuma mensagem retornada."
            mensagem = res.get("message")

            return schemas.MensagemOut(mensagem=mensagem)
        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Erro de validação: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {str(e)}",
            )
