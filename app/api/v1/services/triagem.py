from . import service
from typing import Self
from .. import schemas, clients, utils
from fastapi import HTTPException, status
from pydantic import ValidationError, PositiveInt


class TriagemService(service.Service):
    def __init__(self: Self) -> None:
        super().__init__()
        self.triagem_ixc_cliente = clients.TriagemIXCCliente()

    async def patch_clientes(
        self: Self, id: PositiveInt, cliente: schemas.ClienteIn
    ) -> schemas.MensagemOut:
        try:
            res = await self.triagem_ixc_cliente.get_clientes(id=id)
            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado.",
                )

            cliente_antigo = res["registros"][0]
            novo_cliente = cliente.model_dump(exclude_unset=True)

            cliente_atualizado = {**cliente_antigo, **novo_cliente}

            if "cep" in cliente_atualizado:
                cliente_atualizado["cep"] = utils.formatar_cep(
                    cep=cliente_atualizado["cep"]
                )

            cliente_atualizado.pop("id", None)

            res = await self.triagem_ixc_cliente.patch_clientes(
                id=id, cliente=cliente_atualizado
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
