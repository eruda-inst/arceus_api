from typing import Annotated

from fastapi import APIRouter, Body

from .. import schemas, services, utils

triagem_router = APIRouter(prefix="/triagem", tags=["Triagem"])


@triagem_router.get(
    path="/contato_cliente", summary="Obtém dados de contato de um cliente"
)
async def get_contato_cliente(
    protocolo: utils.Protocolo | None = None, cnpj_cpf: utils.CnpjCpf | None = None
) -> schemas.ContatoOut:
    """
    Obtém dados de contato de um cliente, através do protocolo de atendimento ou CPF/CNPJ
    """
    return await services.TriagemService.get_contato_cliente(
        protocolo=protocolo, cnpj_cpf=cnpj_cpf
    )


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@triagem_router.put(path="/contato_cliente", summary="Atualiza contato de um cliente")
async def put_contato_cliente(
    telefone_celular: Annotated[
        str, Body(embed=True, description="Novo telefone celular")
    ],
    protocolo: utils.Protocolo | None = None,
    cnpj_cpf: utils.CnpjCpf | None = None,
) -> schemas.ContatoOut:
    """
    Atualiza contato de um cliente, através do protocolo de atendimento ou CPF/CNPJ
    """
    return await services.TriagemService.put_contato_cliente(
        protocolo=protocolo, cnpj_cpf=cnpj_cpf, telefone_celular=telefone_celular
    )
