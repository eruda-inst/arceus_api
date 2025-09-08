from fastapi import APIRouter, Query
from app.schemas.contract import ContracListOut
from app.services.aggregator import AggregatorService


router  = APIRouter()
service = AggregatorService()


@router.get("/contratos", response_model=ContracListOut)
def get_contratos_cliente(
    protocolo_atendimento_opa: str = Query(min_length=12, max_length=12, regex="NWT[\d]{9}", description="Protocolo de atendimento do cliente no OpaSuite.")
):
    return service.get_contratos_cliente(protocolo_atendimento_opa)