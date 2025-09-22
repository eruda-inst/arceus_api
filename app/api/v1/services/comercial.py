from datetime import datetime
from typing import Self, Optional
from ..schemas import Meta, Links
from pydantic import ValidationError
from ..clients import ComercialIXCCliente, ComercialOpaCliente
from fastapi import HTTPException, status
from ..utils import rotular_status_acesso, SortOrder
from ..schemas import (
    ComercialContratoListOut,
    ComercialContrato,
    StatusAcessoOut,
    StatusAcesso,
    LeadIn,
    LeadCreate,
)


class Service:
    def __init__(
        self: Self,
    ) -> None:
        self.ixc_cliente = ComercialIXCCliente()
        self.opa_cliente = ComercialOpaCliente()

    async def get_status_acesso(self: Self, id_contrato: int) -> StatusAcessoOut:
        try:
            res = await self.ixc_cliente.get_status_acesso(id_contrato=id_contrato)
            status_acesso = res.get("registros", [])
            if not status_acesso:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sem status de acesso.",
                )
            status_acesso_cod = status_acesso[0].get("status_internet")
            status_acesso_rot = rotular_status_acesso(
                status_acesso_codigo=status_acesso_cod
            )
            return StatusAcessoOut(data=StatusAcesso(status_acesso=status_acesso_rot))
        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Validação da resposta falhou: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    async def get_contratos(
        self: Self,
        protocolo: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "cliente_contrato.id",
        sortorder: Optional[SortOrder] = SortOrder.ASC,
    ):
        try:
            id_cliente_opa_res = await self.opa_cliente.get_id_cliente_opa(
                protocolo=protocolo
            )
            if not id_cliente_opa_res.get("data", []):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado no OPA.",
                )
            id_cliente_opa = id_cliente_opa_res["data"][0]["id_cliente"]

            id_cliente_ixc_res = await self.opa_cliente.get_id_cliente_ixc(
                id_cliente_opa=id_cliente_opa
            )
            if not id_cliente_ixc_res.get("data", []):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado no IXC.",
                )
            id_cliente_ixc = id_cliente_ixc_res["data"][0]["id"]

            contratos_res = await self.ixc_cliente.get_contratos(
                id_cliente=id_cliente_ixc,
                page=page,
                per_page=per_page,
                sortname=sortname,
                sortorder=sortorder,
            )
            if not contratos_res.get("registros", []):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sem contrato.",
                )
            contratos = contratos_res["registros"]

            contratos_tratados = []
            hoje = datetime.now().date()

            for contrato in contratos:
                a_receber_res = await self.ixc_cliente.get_valor_e_data_vencimento(
                    id_contrato=contrato["id"]
                )
                titulos_nao_quitados = [
                    ar
                    for ar in a_receber_res.get("registros", [])
                    if ar.get("status") != "Q"
                ]

                if not titulos_nao_quitados:
                    contrato_tratado = {
                        "id": contrato["id"],
                        "contrato": contrato["contrato"],
                        "valor": 0.00,
                        "status_acesso": rotular_status_acesso(
                            status_acesso_codigo=contrato["status_internet"]
                        ),
                        "data_vencimento": "Não fornecida.",
                    }
                    contratos_tratados.append(contrato_tratado)
                    continue

                proximo_vencimento = None
                menor_diferenca = None

                for titulo in titulos_nao_quitados:
                    data_vencimento_str = titulo.get("data_vencimento")
                    if data_vencimento_str:
                        try:
                            data_vencimento = datetime.strptime(
                                data_vencimento_str, "%Y-%m-%d"
                            ).date()
                            diferenca = (data_vencimento - hoje).days

                            if diferenca >= 0 and (
                                menor_diferenca is None or diferenca < menor_diferenca
                            ):
                                menor_diferenca = diferenca
                                proximo_vencimento = titulo
                        except ValueError:
                            continue

                titulo_final = proximo_vencimento
                if not titulo_final:
                    titulo_final = max(
                        titulos_nao_quitados,
                        key=lambda x: datetime.strptime(
                            x.get("data_vencimento"), "%Y-%m-%d"
                        ).date(),
                    )

                contrato_tratado = {
                    "id": contrato["id"],
                    "contrato": contrato["contrato"],
                    "valor": titulo_final.get("valor"),
                    "status_acesso": rotular_status_acesso(
                        status_acesso_codigo=contrato["status_internet"]
                    ),
                    "data_vencimento": titulo_final.get("data_vencimento"),
                }
                contratos_tratados.append(contrato_tratado)

            total = contratos.__len__()

            meta = Meta(
                total=total,
                page=page,
                per_page=per_page,
            )

            base_url = f"/contratos?protocolo={protocolo}"
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

            return ComercialContratoListOut(
                data=[ComercialContrato(**ct) for ct in contratos_tratados],
                meta=meta,
                links=links,
            )

        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Validação da resposta falhou: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    async def post_lead(self: Self, lead: LeadIn) -> LeadCreate:
        try:
            res = await self.ixc_cliente.post_lead(lead=lead)
            id_lead = res.get("id", None)
            return LeadCreate(id=id_lead)
        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Validação da resposta falhou: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )
