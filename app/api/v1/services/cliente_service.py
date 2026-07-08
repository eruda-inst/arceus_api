from typing import Any
from .. import clients, utils
from fastapi import HTTPException, status


class ClienteService:
    @staticmethod
    async def get_cliente_ixc(
        protocolo: str | None = None, cnpj_cpf: str | None = None
    ) -> dict[str, Any]:
        try:
            if cnpj_cpf:
                endpoint = "cliente"
                cnpj_cpf_formatado = utils.Formatter.cnpj_cpf(cnpj_cpf=cnpj_cpf)
                grid_param = [
                    {"TB": "cliente.cnpj_cpf", "OP": "=", "P": cnpj_cpf_formatado}
                ]
                res = await clients.IXCCliente.get(
                    endpoint=endpoint, grid_param=grid_param
                )
                regs = res.get("registros", [])
                if not regs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cliente inexistente no IXC.",
                    )
                cliente_ixc = regs[0]
                return cliente_ixc
            elif protocolo:
                endpoint = "atendimento"
                filter = {"protocolo": protocolo}
                res = await clients.OpaCliente.get(endpoint=endpoint, filter=filter)
                data = res.get("data", [])
                if not data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cliente inexistente no Opa.",
                    )
                cliente_opa = data[0]
                id = cliente_opa["id_cliente"]

                endpoint = "cliente"
                filter = {"_id": id}
                res = await clients.OpaCliente.get(endpoint=endpoint, filter=filter)
                data = res.get("data", [])
                if not data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cliente inexistente no IXC.",
                    )
                cliente_opa = data[0]

                endpoint = "cliente"
                id_cliente_ixc = cliente_opa["id"]
                grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id_cliente_ixc)}]
                res = await clients.IXCCliente.get(
                    endpoint=endpoint, grid_param=grid_param
                )
                regs = res.get("registros", [])
                if not regs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Cliente inexistente no IXC.",
                    )
                cliente_ixc = regs[0]
                return cliente_ixc
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Forneça cnpj_cpf ou protocolo.",
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )
