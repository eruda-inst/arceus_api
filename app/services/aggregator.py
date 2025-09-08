from typing import Optional
from app.clients.ixc import IXCClient
from app.clients.opa import OpaClient
from fastapi import HTTPException, status
from app.schemas.contract import ContracListOut
from app.schemas.conexao import StatusConexao, StatusConexaoOut


class AggregatorService:
    def __init__(self):
        self.opa_client = OpaClient()
        self.ixc_client = IXCClient()


    def get_contratos_cliente(self, protocolo_atendimento_opa: str) -> Optional[ContracListOut]:
        try:
            id_cliente_opa_res = self.opa_client.get_id_cliente_opa(protocolo_atendimento_opa)
            if not id_cliente_opa_res.get("data"):
                raise HTTPException(status_code=404, detail="Cliente não encontrado no OPA")
            id_cliente_opa = id_cliente_opa_res["data"][0]["id_cliente"]

            id_cliente_ixc_res = self.opa_client.get_id_cliente_ixc(id_cliente_opa)
            if not id_cliente_ixc_res.get("data"):
                raise HTTPException(status_code=404, detail="Cliente não encontrado no IXC")
            id_cliente_ixc = id_cliente_ixc_res["data"][0]["id"]

            contratos_res = self.ixc_client.get_contratos_cliente(id_cliente_ixc)
            return ContracListOut(data=contratos_res.get("registros", []))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}"
            )
        
    def get_status_conexao(self, id_login_ixc: int) -> StatusConexaoOut:
        try:
            status_conexao_res = self.ixc_client.get_status_conexao(id_login_ixc)
            registros = status_conexao_res.get("registros", [])
            if not registros:
                raise HTTPException(status_code=404, detail="Nenhum registro.")
            status_conexao = registros[0].get("online")

            return StatusConexaoOut(data=StatusConexao(status_conexao=status_conexao))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}"
            )