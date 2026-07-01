from typing import Any
from . import service_service
from .. import schemas, clients, utils
from fastapi import HTTPException, status


class TriagemService(service_service.Service):
    @classmethod
    async def get_contato_cliente(
        cls, protocolo: str | None = None, cnpj_cpf: str | None = None
    ) -> schemas.ContatoOut:
        try:
            id_cliente = await cls.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id_cliente)}]

            res = await clients.IXCCliente.get(
                endpoint="cliente", grid_param=grid_param
            )
            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado.",
                )

            contato = res["registros"][0]["telefone_celular"]
            return schemas.ContatoOut(telefone_celular=contato)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {str(e)}",
            )

    @classmethod
    async def put_contato_cliente(
        cls,
        telefone_celular: str,
        protocolo: str | None = None,
        cnpj_cpf: str | None = None,
    ) -> schemas.MensagemOut:
        try:
            id_cliente = await cls.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id_cliente)}]

            res = await clients.IXCCliente.get(
                endpoint="cliente", grid_param=grid_param
            )

            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado.",
                )

            cliente_antigo = res["registros"][0]

            cliente_atualizado: Any = {
                **cliente_antigo,
                "telefone_celular": utils.Formatter.cell(cell=telefone_celular),
            }

            if "cep" in cliente_atualizado:
                cliente_atualizado["cep"] = utils.Formatter.cep(
                    cep=cliente_atualizado["cep"]
                )

            del cliente_atualizado["id"]

            res = await clients.IXCCliente.put(
                endpoint="cliente", id=id_cliente, payload=cliente_atualizado
            )

            mensagem = "Nenhuma mensagem retornada."
            mensagem = res.get("message")

            return schemas.MensagemOut(mensagem=mensagem)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {str(e)}",
            )
