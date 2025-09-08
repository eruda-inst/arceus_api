from typing import Optional
from app.clients.ixc import IXCClient
from app.clients.opa import OpaClient
from fastapi import HTTPException, status
from app.schemas.conexao import StatusConexao, StatusConexaoOut
from app.schemas.contract import ContracListOut, Meta, Links, Contract


class AggregatorService:
    def __init__(self):
        self.opa_client = OpaClient()
        self.ixc_client = IXCClient()


    def get_contratos_cliente(
        self, protocolo_atendimento_opa: str, page: int = 1, per_page: int = 10
    ) -> Optional[ContracListOut]:
        try:
            id_cliente_opa_res = self.opa_client.get_id_cliente_opa(protocolo_atendimento_opa)
            if not id_cliente_opa_res.get("data"):
                raise HTTPException(status_code=404, detail="Cliente não encontrado no OPA")
            id_cliente_opa = id_cliente_opa_res["data"][0]["id_cliente"]

            id_cliente_ixc_res = self.opa_client.get_id_cliente_ixc(id_cliente_opa)
            if not id_cliente_ixc_res.get("data"):
                raise HTTPException(status_code=404, detail="Cliente não encontrado no IXC")
            id_cliente_ixc = id_cliente_ixc_res["data"][0]["id"]

            contratos_res = self.ixc_client.get_contratos_cliente(id_cliente_ixc, page, per_page)
            registros = contratos_res.get("registros", [])
            total = contratos_res.get("total", len(registros))

            total_raw = contratos_res.get("total", len(registros))
            try:
                total = int(total_raw)
            except (TypeError, ValueError):
                total = len(registros)
            meta = Meta(total=total, page=page, per_page=per_page)

            base_url = f"/contratos?protocolo_atendimento_opa={protocolo_atendimento_opa}"
            links = Links(
                self=f"{base_url}&page={page}&per_page={per_page}",
                next=(f"{base_url}&page={page+1}&per_page={per_page}" if page * per_page < total else None),
                prev=(f"{base_url}&page={page-1}&per_page={per_page}" if page > 1 else None),
            )

            return ContracListOut(
                data=[Contract(**c) for c in registros],
                meta=meta,
                links=links
            )
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