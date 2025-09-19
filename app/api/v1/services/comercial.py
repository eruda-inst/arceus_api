from typing import Self
from pydantic import ValidationError
from fastapi import HTTPException, status
from ..utils import rotular_status_acesso
from ..clients import IXCClient, OpaClient
from ..schemas import StatusAcesso, StatusAcessoOut


class Service:
    def __init__(
        self: Self,
    ) -> None:
        self.opa_client = OpaClient()
        self.ixc_client = IXCClient()

    async def get_status_acesso(
        self: Self,
        id_contrato: int,
    ) -> StatusAcessoOut:
        try:
            res = await self.ixc_client.get_status_acesso(id_contrato=id_contrato)
            reg = res.get("registros", [])
            if not reg:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sem status de acesso."
                )
            status_acesso_cod = reg[0].get("status_internet")
            status_acesso_rot = rotular_status_acesso(status_acesso_codigo=status_acesso_cod)
            return StatusAcessoOut(data=StatusAcesso(status_acesso=status_acesso_rot))
        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Validação da resposta falhou: {e}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}"
            )