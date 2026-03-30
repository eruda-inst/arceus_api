from typing import Optional
from .. import schemas, services
from fastapi import APIRouter, Body, Query


triagem_router = APIRouter(prefix="/triagem", tags=["Triagem"])
triagem_service = services.TriagemService()


@triagem_router.get(
    path="/contato_cliente",
    response_model=schemas.ContatoOut,
    summary="Busca os dados de contato de um cliente específico.",
    description="Busca os dados de contato de um cliente específico, baseado no protocolo de atendimento ou no CPF/CNPJ.",
)
async def get_contato_cliente(
    protocolo: Optional[str] = Query(
        default=None,
        min_length=12,
        max_length=12,
        description="Protocolo de atendimento.",
    ),
    cnpj_cpf: Optional[str] = Query(
        default=None, description="CPF ou CNPJ do cliente."
    ),
) -> schemas.ContatoOut:
    return await triagem_service.get_contato_cliente(
        protocolo=protocolo, cnpj_cpf=cnpj_cpf
    )


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@triagem_router.put(
    path="/contato_cliente",
    response_model=schemas.MensagemOut,
    summary="Atualiza um ou mais campos associado a um cliente específico.",
    description="Atualiza um ou mais campos associado a um cliente específico, baseado no protocolo de atendimento ou no CPF/CNPJ.",
)
async def put_contato_cliente(
    protocolo: Optional[str] = Query(
        default=None,
        min_length=12,
        max_length=12,
        description="Protocolo de atendimento.",
    ),
    cnpj_cpf: Optional[str] = Query(
        default=None, description="CPF ou CNPJ do cliente."
    ),
    contato: schemas.ContatoUpdate = Body(
        description="Campos de cliente a serem atualizados."
    ),
) -> schemas.MensagemOut:
    return await triagem_service.put_contato_cliente(
        protocolo=protocolo, cnpj_cpf=cnpj_cpf, contato=contato
    )
