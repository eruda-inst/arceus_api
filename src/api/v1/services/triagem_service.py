from typing import Any

from fastapi import HTTPException, status

from .. import clients, schemas, utils
from . import ClientService


class TriagemService:
    @staticmethod
    async def get_contato_cliente(
        protocolo: str | None, cnpj_cpf: str | None
    ) -> schemas.ContatoOutSchema:
        # --- Obtém cliente ---
        cliente = await ClientService.get_cliente_ixc(
            protocolo=protocolo, cnpj_cpf=cnpj_cpf
        )

        return schemas.ContatoOutSchema(telefone_celular=cliente["telefone_celular"])

    @staticmethod
    async def put_contato_cliente(
        telefone_celular: str,
        protocolo: str | None = None,
        cnpj_cpf: str | None = None,
    ) -> schemas.ContatoOutSchema:
        # --- Obtém cliente atual ---
        cliente_antigo = await ClientService.get_cliente_ixc(
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
        res = await clients.IxcClient.put(
            endpoint=endpoint, id=cliente_antigo["id"], payload=cliente_atualizado
        )
        if res["type"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Atualização malsucedida",
            )

        return schemas.ContatoOutSchema(telefone_celular=telefone_celular)
