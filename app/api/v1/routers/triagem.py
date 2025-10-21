from typing import Optional
from .. import schemas, services
from fastapi import APIRouter, Body, Query


triagem_router = APIRouter()
triagem_service = services.TriagemService()


@triagem_router.get(
    path="/contato_cliente",
    response_model=schemas.ContatoOut,
    summary="Busca os dados de contato de um cliente específico, baseado no protocolo de atendimento e no CPF/CNPJ.",
)
async def get_contato_cliente(
    protocolo: Optional[str] = Query(
        default=None, description="Protocolo de atendimento."
    ),
    cnpj_cpf: Optional[str] = Query(
        default=None, description="CPF ou CNPJ do cliente."
    ),
) -> schemas.ContatoOut:
    """
    Busca os dados de contato de um cliente específico.

    Args:
        protocolo: O protocolo de atendimento.
        cnpj_cpf: O CPF ou CNPJ do cliente.

    Returns:
        Os dados do cliente.
    """
    return await triagem_service.get_contato_cliente(
        protocolo=protocolo, cnpj_cpf=cnpj_cpf
    )


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@triagem_router.put(
    path="/contato_cliente",
    response_model=schemas.MensagemOut,
    summary="Atualiza um ou mais campos associado a um cliente específico, baseado no protocolo de atendimento.",
)
async def put_contato_cliente(
    protocolo: str = Query(description="Protocolo de atendimento."),
    contato: schemas.ContatoUpdate = Body(
        description="Campos de cliente a serem atualizados."
    ),
) -> schemas.MensagemOut:
    """
    Atualiza os dados de contato de um cliente específico.

    Args:
        protocolo: O protocolo de atendimento.
        contato: Os novos dados de contato do cliente.

    Returns:
        Uma mensagem de confirmação da atualização.
    """
    return await triagem_service.put_contato_cliente(
        protocolo=protocolo, contato=contato
    )
