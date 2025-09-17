from typing import Optional
from ..services import AggregatorService
from fastapi import APIRouter, Query, status
from ..schemas import StatusConexaoOut, AtendimentoOut, AtendimentoIn, ContratoListOut, StatusContratoOut, StatusONUOut, AtendimentoCreate


router  = APIRouter()
service = AggregatorService()

@router.get("/contratos_ativos_cliente", response_model=ContratoListOut, summary="Obtém contratos ativos de um cliente, através de protocolo de atendimento.")
async def get_contratos_ativos_cliente(
    protocolo_atendimento_opa: str = Query(min_length=12, max_length=12, description="Protocolo de atendimento do cliente no OpaSuite."),
    page: Optional[int] = Query(ge=1, default=1, description="Número da página."),
    per_page: Optional[int] = Query(ge=1, default=10, description="Itens por página."),
):
    return await service.get_contratos_ativos_cliente(protocolo_atendimento_opa, page, per_page)

@router.get("/status_conexao", response_model=StatusConexaoOut, summary="Obtém status de conexão de um cliente, através de ID de login.")
async def get_status_conexao(
    id_login_ixc: int = Query(description="ID de login do cliente no IXCSoft."),
):
    return await service.get_status_conexao(id_login_ixc)

@router.get("/status_contrato", response_model=StatusContratoOut, summary="Obtém status de contrato de um cliente, através de ID de contrato.")
async def get_status_contrato(
    id_contrato_ixc: int = Query(description="ID de contrato do cliente no IXCSoft."),
):
    return await service.get_status_contrato(id_contrato_ixc)

@router.get("/status_onu", response_model=StatusONUOut, summary="Obtém status de ONU (sinal rx e tx) de um cliente, através de ID de login, ou MAC Address de ONU.")
async def get_status_onu(
    id_login_ixc: Optional[int] = Query(default=None, description="ID de login do cliente no IXCSoft."),
    mac_onu_ixc: Optional[str] = Query(default=None, description="MAC Address da ONU."),
):
    return await service.get_status_onu(id_login_ixc, mac_onu_ixc)

@router.post("/enviar_sinal_desconexao", status_code=status.HTTP_204_NO_CONTENT, summary="Envia sinal de desconexão para um cliente, através de ID de login.")
async def enviar_sinal_desconexao(
    id_login_ixc: int = Query(description="ID de login do cliente no IXCSoft."),
):
    return await service.enviar_sinal_desconexao(id_login_ixc)

@router.get("/checar_atendimentos_abertos", response_model=AtendimentoOut, summary="Checa atendimentos abertos de um cliente, através de ID de login.")
async def checar_atendimentos_abertos(
    id_login_ixc: int = Query(description="ID de login do cliente no IXCSoft."),
    page: Optional[int] = Query(ge=1, default=1, description="Número da página."),
    per_page: Optional[int] = Query(ge=1, default=10, description="Itens por página."),
):
    await service.checar_atendimentos_abertos(id_login_ixc, page, per_page)

@router.post("/abrir_atendimento", summary="Abre ticket de atendimento, através de dados do atendimento.")
async def abrir_atendimento(
    atendimento: AtendimentoIn,
) -> AtendimentoCreate:
    return await service.abrir_atendimento(atendimento)