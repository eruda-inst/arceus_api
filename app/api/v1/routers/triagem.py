from .. import schemas, services
from pydantic import PositiveInt
from fastapi import APIRouter, Path, Body


triagem_router = APIRouter()
triagem_service = services.TriagemService()


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@triagem_router.put(
    path="/contato_cliente/{id_cliente}",
    response_model=schemas.MensagemOut,
    summary="Atualiza um ou mais campos associado a um cliente específico, por meio do ID de cliente.",
)
async def put_contato_cliente(
    id_cliente: PositiveInt = Path(ge=1, description="ID de cliente."),
    contato: schemas.ContatoUpdate = Body(
        description="Campos de cliente a serem atualizados."
    ),
) -> schemas.MensagemOut:
    """
    Atualiza os dados de contato de um cliente específico.

    Args:
        id_cliente: O ID do cliente a ser atualizado.
        contato: Os novos dados de contato do cliente.

    Returns:
        Uma mensagem de confirmação da atualização.
    """
    return await triagem_service.put_contato_cliente(
        id_cliente=id_cliente, contato=contato
    )
