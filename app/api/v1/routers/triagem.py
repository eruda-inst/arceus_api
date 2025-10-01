from .. import schemas, services
from pydantic import PositiveInt
from fastapi import APIRouter, Path, Body


triagem_router = APIRouter()
triagem_service = services.TriagemService()


# Por razões de limitações na plataforma opa, o verbo deve ser put, ao invés de patch
@triagem_router.put(
    path="/clientes/{id}",
    response_model=schemas.MensagemOut,
    summary="Atualiza um ou mais campos associado a um cliente específico, por meio do ID de cliente.",
)
async def patch_clientes(
    id: PositiveInt = Path(ge=1, description="ID de cliente."),
    cliente: schemas.ClienteIn = Body(
        description="Campos de cliente a serem atualizados."
    ),
) -> schemas.MensagemOut:
    return await triagem_service.patch_clientes(id=id, cliente=cliente)
