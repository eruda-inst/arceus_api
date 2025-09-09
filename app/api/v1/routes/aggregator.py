from typing import Optional
from fastapi import APIRouter, Query
from app.schemas.onu import StatusONUOut
from app.schemas.conexao import StatusConexaoOut
from app.services.aggregator import AggregatorService
from app.schemas.contrato import ContracListOut, StatusContratoOut


router  = APIRouter()
service = AggregatorService()


@router.get("/contratos", response_model=ContracListOut)
async def get_contratos_cliente(
    protocolo_atendimento_opa: str = Query(min_length=12, max_length=12, description="Protocolo de atendimento do cliente no OpaSuite."),
    page: int = Query(ge=1, default=1, description="Número da página."),
    per_page: int = Query(ge=1, default=10, description="Itens por página.")
):
    return await service.get_contratos_cliente(protocolo_atendimento_opa, page, per_page)


@router.get("/status_conexao", response_model=StatusConexaoOut)
async def get_status_conexao(
    id_login_ixc: int = Query(ge=1, description="ID de login do cliente no IXCSoft.")
):
    return await service.get_status_conexao(id_login_ixc)


@router.get("/status_contrato", response_model=StatusContratoOut)
async def get_status_contrato(
    id_contrato_ixc: int = Query(ge=1, description="ID de contrato do cliente no IXCSoft.")
):
    return await service.get_status_contrato(id_contrato_ixc)


@router.get("/status_onu", response_model=StatusONUOut)
async def get_status_onu(
    id_login_ixc: Optional[int] = Query(default=None, ge=1, description="ID de login do cliente no IXCSoft."),
    mac_onu_ixc: Optional[str] = Query(default=None, max_length=50, description="MAC Address da ONU.")
):
    return await service.get_status_onu(id_login_ixc, mac_onu_ixc)