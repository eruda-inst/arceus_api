from fastapi import APIRouter, Query
from app.schemas.contract import ContracListOut
from app.services.aggregator import AggregatorService


router  = APIRouter()
service = AggregatorService()


@router.get("/contratos", response_model=ContracListOut)
def get_contratos_cliente(
    protocolo_atendimento_opa: str = Query(min_length=12, max_length=12, description="Protocolo de atendimento do cliente no OpaSuite."),
    page: int = Query(ge=1, default=1, description="Número da página."),
    per_page: int = Query(ge=1, default=10, description="Itens por página.")
):
    return service.get_contratos_cliente(protocolo_atendimento_opa, page, per_page)


@router.get("/status_conexao")
def get_status_conexao(
    id_login_ixc: int = Query(ge=1, description="")
):
    return service.get_status_conexao(id_login_ixc)