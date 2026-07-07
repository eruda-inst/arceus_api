from . import Service
from typing import Any
from .. import schemas, clients, utils
from fastapi import HTTPException, status


class TriagemService:
    @staticmethod
    async def get_contato_cliente(
        protocolo: str | None, cnpj_cpf: str | None
    ) -> schemas.ContatoOut:
        try:
            id_cliente = await Service.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            # --- Cliente ---
            endpoint = "cliente"
            grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id_cliente)}]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Cliente inexistente."
                )
            cliente = regs[0]

            # --- Contato ---
            telefone_celular = cliente["telefone_celular"]

            return schemas.ContatoOut(telefone_celular=telefone_celular)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def put_contato_cliente(
        telefone_celular: str,
        protocolo: str | None = None,
        cnpj_cpf: str | None = None,
    ) -> schemas.ContatoOut:
        try:
            id_cliente = await Service.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            # --- Cliente ---
            endpoint = "cliente"
            grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id_cliente)}]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Cliente inexistente."
                )
            cliente_antigo = regs[0]

            # --- Cliente atualizado ---
            cliente_atualizado: dict[str, Any] = {
                **cliente_antigo,
                "telefone_celular": utils.Formatter.cell(cell=telefone_celular),
            }
            del cliente_atualizado["id"]

            # --- Atualiza cliente ---
            res = await clients.IXCCliente.put(
                endpoint=endpoint, id=id_cliente, payload=cliente_atualizado
            )
            type = res["type"]
            if type == "error":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Atualização malsucedida.",
                )

            return schemas.ContatoOut(telefone_celular=telefone_celular)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )
