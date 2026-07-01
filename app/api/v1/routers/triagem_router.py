from typing import Annotated
from .. import schemas, services
from fastapi import APIRouter, Body, Query

triagem_router = APIRouter(prefix="/triagem", tags=["Triagem"])


@triagem_router.get(
    path="/contato_cliente",
    summary="Busca os dados de contato de um cliente específico.",
)
async def get_contato_cliente(
    protocolo: Annotated[
        str | None,
        Query(min_length=12, max_length=12, description="Protocolo de atendimento."),
    ] = None,
    cnpj_cpf: Annotated[
        str | None, Query(description="CPF ou CNPJ do cliente.")
    ] = None,
) -> schemas.ContatoOut:
    """
    Busca os dados de contato de um cliente específico, baseado no protocolo de atendimento ou no CPF/CNPJ.
    """
    return await services.TriagemService.get_contato_cliente(
        protocolo=protocolo, cnpj_cpf=cnpj_cpf
    )


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@triagem_router.put(
    path="/contato_cliente",
    summary="Atualiza contato de um cliente.",
)
async def put_contato_cliente(
    telefone_celular: Annotated[
        str,
        Body(embed=True, description="Campos de cliente a serem atualizados."),
    ],
    protocolo: Annotated[
        str | None,
        Query(min_length=12, max_length=12, description="Protocolo de atendimento."),
    ] = None,
    cnpj_cpf: Annotated[
        str | None, Query(description="CPF ou CNPJ do cliente.")
    ] = None,
) -> schemas.MensagemOut:
    """
    Atualiza contato de um cliente, baseado no protocolo de atendimento ou no CPF/CNPJ.
    """
    return await services.TriagemService.put_contato_cliente(
        protocolo=protocolo, cnpj_cpf=cnpj_cpf, telefone_celular=telefone_celular
    )
