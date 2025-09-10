from datetime import datetime
from app.clients.ixc import IXCClient
from app.clients.opa import OpaClient
from fastapi import HTTPException, status
from app.schemas.atendimento import AtendimentoIn
from app.schemas.onu import StatusONU, StatusONUOut
from app.utils.helpers.rotular import rotular_status_conexao
from app.schemas.conexao import StatusConexao, StatusConexaoOut
from app.schemas.contrato import ContratoListOut, Meta, Links, Contrato, StatusContratoOut, StatusContrato


class AggregatorService:
    def __init__(self):
        self.opa_client = OpaClient()
        self.ixc_client = IXCClient()


    async def get_contratos_ativos_cliente(
        self, protocolo_atendimento_opa: str, page: int = 1, per_page: int = 10
    ) -> ContratoListOut:
        try:
            id_cliente_opa_res = self.opa_client.get_id_cliente_opa(protocolo_atendimento_opa)
            if not id_cliente_opa_res.get("data"):
                raise HTTPException(status_code=404, detail="Cliente não encontrado no OPA")
            id_cliente_opa = id_cliente_opa_res["data"][0]["id_cliente"]

            id_cliente_ixc_res = self.opa_client.get_id_cliente_ixc(id_cliente_opa)
            if not id_cliente_ixc_res.get("data"):
                raise HTTPException(status_code=404, detail="Cliente não encontrado no IXC")
            id_cliente_ixc = id_cliente_ixc_res["data"][0]["id"]

            contratos_res = await self.ixc_client.get_contratos_ativos_cliente(id_cliente_ixc, page, per_page)
            registros = contratos_res.get("registros", [])

            registros_ativos = [r for r in registros if r["status"] not in ("I", "D")]
            total = len(registros_ativos)
            
            for contrato in registros_ativos:
                a_receber_res = await self.ixc_client.valor_e_data_vencimento(contrato["id"])
                registros = a_receber_res.get("registros", [])
                
                titulos_nao_quitados = [r for r in registros if r.get("status") != 'Q']
                
                if not titulos_nao_quitados:
                    contrato["valor"] = None
                    contrato["data_vencimento"] = None
                    continue

                hoje = datetime.now().date()
                proximo_vencimento = None
                menor_diferenca = None

                for titulo in titulos_nao_quitados:
                    data_vencimento_str = titulo.get("data_vencimento")
                    if data_vencimento_str:
                        try:
                            data_vencimento = datetime.strptime(data_vencimento_str, "%Y-%m-%d").date()
                            diferenca = (data_vencimento - hoje).days
                            
                            if diferenca >= 0:
                                if menor_diferenca is None or diferenca < menor_diferenca:
                                    menor_diferenca = diferenca
                                    proximo_vencimento = titulo
                        except ValueError:
                            continue

                if proximo_vencimento:
                    contrato["valor"] = proximo_vencimento.get("valor")
                    contrato["data_vencimento"] = proximo_vencimento.get("data_vencimento")
                else:
                    ultimo_titulo = max(titulos_nao_quitados, key=lambda x: datetime.strptime(x.get("data_vencimento"), "%Y-%m-%d").date())
                    contrato["valor"] = ultimo_titulo.get("valor")
                    contrato["data_vencimento"] = ultimo_titulo.get("data_vencimento")
            meta = Meta(total=total, page=page, per_page=per_page)
            base_url = f"/contratos?protocolo_atendimento_opa={protocolo_atendimento_opa}"
            links = Links(
                self=f"{base_url}&page={page}&per_page={per_page}",
                next=(
                    f"{base_url}&page={page + 1}&per_page={per_page}"
                    if (page * per_page) < total
                    else None
                ),
                prev=(
                    f"{base_url}&page={page - 1}&per_page={per_page}"
                    if page > 1
                    else None
                ),
            )
            return ContratoListOut(
                data=[Contrato(**contrato) for contrato in registros_ativos],
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
        

    async def get_status_conexao(self, id_login_ixc: int) -> StatusConexaoOut:
        try:
            status_conexao_res = await self.ixc_client.get_status_conexao(id_login_ixc)
            registros = status_conexao_res.get("registros", [])
            if not registros:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Nenhum registro."
                )
            status_conexao = registros[0].get("online")
            status_conexao = rotular_status_conexao(status_conexao)
            return StatusConexaoOut(
                data=StatusConexao(
                    status_conexao=status_conexao
                )
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}"
            )


    async def get_status_contrato(self, id_contrato_ixc: int) -> StatusContratoOut:
        try:
            status_contrato_res = await self.ixc_client.get_status_contrato(id_contrato_ixc)
            registros = status_contrato_res.get("registros", [])
            if not registros:
                raise HTTPException(
                    status=status.HTTP_404_NOT_FOUND,
                    detail="Nenhum contrato."
                )
            status_contrato = registros[0].get("status")
            return StatusContratoOut(
                data=StatusContrato(
                    status_contrato=status_contrato
                )
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}"
            )
        

    async def get_status_onu(self, id_login_ixc: int, mac_onu_ixc: str) -> StatusONUOut:
        try:
            if not id_login_ixc and not mac_onu_ixc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="É necessário informar id_login_ixc ou mac_onu_ixc."
                )
            status_onu_res = await self.ixc_client.get_status_onu(id_login_ixc, mac_onu_ixc)
            registros = status_onu_res.get("registros", [])
            if not registros:
                raise HTTPException(
                    status=status.HTTP_404_NOT_FOUND,
                    detail="Nenhuma ONU."
                )
            sinal_rx = registros[0].get("sinal_rx")
            sinal_tx = registros[0].get("sinal_tx")
            return StatusONUOut(
                data=StatusONU(
                    sinal_rx=sinal_rx,
                    sinal_tx=sinal_tx
                )
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}"
            )
        

    async def abrir_atendimento(self, atendimento: AtendimentoIn) -> None:
        try:
            await self.ixc_client.abrir_atendimento(atendimento)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}"
            )
        

    async def enviar_sinal_desconexao(self, id_login_ixc: input):
        try:
            await self.ixc_client.enviar_sinal_desconexao(id_login_ixc)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}"
            )