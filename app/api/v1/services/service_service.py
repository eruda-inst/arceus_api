from typing import Any
from .. import clients, utils
from pydantic import PositiveInt
from fastapi import HTTPException, status


class Service:
    @staticmethod
    async def _buscar_por_protocolo(protocolo: str) -> Any:
        # Busca ID do cliente no OPA
        endpoint = "atendimento"
        filter = {"protocolo": protocolo}
        id_cliente_opa_res = await clients.OpaCliente.get(
            endpoint=endpoint, filter=filter
        )

        if not id_cliente_opa_res.get("data"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado no OPA.",
            )

        id_cliente_opa = id_cliente_opa_res["data"][0]["id_cliente"]

        # Busca ID do cliente no IXC via OPA
        endpoint = "cliente"
        filter = {"_id": id_cliente_opa}
        id_cliente_ixc_res = await clients.OpaCliente.get(
            endpoint=endpoint, filter=filter
        )

        if not id_cliente_ixc_res.get("data"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado no IXC através do protocolo OPA.",
            )

        return id_cliente_ixc_res

    @staticmethod
    async def _buscar_por_cnpj_cpf(cnpj_cpf: str) -> Any:
        endpoint = "cliente"
        grid_param = [{"TB": "cliente.cnpj_cpf", "OP": "=", "P": str(cnpj_cpf)}]
        id_cliente_ixc_res = await clients.IXCCliente.get(
            endpoint=endpoint, grid_param=grid_param
        )

        if not id_cliente_ixc_res.get("registros"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado no IXC através do CNPJ/CPF.",
            )

        return id_cliente_ixc_res

    @staticmethod
    def _extrair_id_cliente_ixc(resposta: Any) -> PositiveInt:
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

    @classmethod
    async def get_id_cliente_ixc(
        cls, protocolo: str | None = None, cnpj_cpf: str | None = None
    ) -> PositiveInt:
        try:

            cnpj_cpf_formatado = (
                utils.Formatter.cnpj_cpf(cnpj_cpf=cnpj_cpf) if cnpj_cpf else None
            )

            if not protocolo and not cnpj_cpf_formatado:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Protocolo ou CPF/CNPJ devem ser fornecidos.",
                )

            id_cliente_ixc_res = None

            if protocolo:
                id_cliente_ixc_res = await cls._buscar_por_protocolo(protocolo)
            elif cnpj_cpf_formatado:
                id_cliente_ixc_res = await cls._buscar_por_cnpj_cpf(cnpj_cpf_formatado)

            return cls._extrair_id_cliente_ixc(id_cliente_ixc_res)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )
