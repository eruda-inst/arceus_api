from typing import Any
from . import ClienteService
from .. import schemas, clients, utils
from fastapi import HTTPException, status


class TriagemService:
    @staticmethod
    async def get_contato_cliente(
        protocolo: str | None, cnpj_cpf: str | None
    ) -> schemas.ContatoOut:
        try:
            if not protocolo and not cnpj_cpf:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Informe protocolo ou cnpj_cpf.",
                )

            # --- Obtém cliente ---
            cliente = await ClienteService.get_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            return schemas.ContatoOut(telefone_celular=cliente["telefone_celular"])
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )

    @staticmethod
    async def put_contato_cliente(
        telefone_celular: str,
        protocolo: str | None = None,
        cnpj_cpf: str | None = None,
    ) -> schemas.ContatoOut:
        try:
            if not protocolo and not cnpj_cpf:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Informe protocolo ou cnpj_cpf.",
                )

            # --- Obtém cliente atual ---
            cliente_antigo = await ClienteService.get_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            # Cliente atualizado
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
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )
