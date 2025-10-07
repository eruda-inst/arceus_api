from .. import clients
from typing import Self
from fastapi import HTTPException, status
from pydantic import ValidationError, PositiveInt


class Service:
    def __init__(self: Self) -> None:
        self.opa_cliente = clients.OpaCliente()

    async def get_id_cliente_ixc(self: Self, protocolo: str) -> PositiveInt:
        try:
            id_cliente_opa_res = await self.opa_cliente.get_id_cliente_opa(
                protocolo=protocolo
            )
            if not id_cliente_opa_res.get("data", []):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado no OPA.",
                )
            id_cliente_opa = id_cliente_opa_res["data"][0]["id_cliente"]

            id_cliente_ixc_res = await self.opa_cliente.get_id_cliente_ixc(
                id_cliente_opa=id_cliente_opa
            )
            if not id_cliente_ixc_res.get("data", []):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado no IXC.",
                )
            id_cliente_ixc = id_cliente_ixc_res["data"][0]["id"]
            return id_cliente_ixc
        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Validação da resposta falhou: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )
