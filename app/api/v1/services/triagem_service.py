from . import ClienteService
from typing import Any
from .. import schemas, clients, utils
from fastapi import HTTPException, status


class TriagemService:
    @staticmethod
    async def get_contato_cliente(
        protocolo: str | None, cnpj_cpf: str | None
    ) -> schemas.ContatoOut:
        try:
            # --- Cliente ---
            cliente = await ClienteService.get_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

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
            # --- Cliente ---
            cliente_antigo = await ClienteService.get_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            # --- Cliente atualizado ---
            cliente_atualizado: dict[str, Any] = {
                **cliente_antigo,
                "telefone_celular": utils.Formatter.cell(cell=telefone_celular),
            }
            del cliente_atualizado["id"]

            # --- Atualiza cliente ---
            endpoint = "cliente"
            res = await clients.IxcCliente.put(
                endpoint=endpoint, id=cliente_antigo["id"], payload=cliente_atualizado
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
