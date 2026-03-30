from . import service_service
from typing import Self, Optional, Any
from .. import clients, schemas, utils
from fastapi import HTTPException, status
from pydantic import ValidationError, PositiveInt


class FinanceiroService(service_service.Service):
    def __init__(self: Self) -> None:
        super().__init__()
        self.financeiro_ixc_cliente = clients.FinanceiroIXCCliente()
        self.financeiro_az7_cliente = clients.FinanceiroAZ7Cliente()

    async def get_faturas_abertas(
        self: Self,
        protocolo: Optional[str] = None,
        cnpj_cpf: Optional[str] = None,
        page: Optional[PositiveInt] = 1,
        per_page: Optional[PositiveInt] = 15,
        sortname: Optional[str] = "fn_areceber.id",
        sortorder: Optional[utils.SortOrder] = utils.SortOrder.ASC,
    ) -> schemas.FaturaAbertaListOut:
        try:
            id_cliente = await self.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            res = await self.financeiro_ixc_cliente.get_faturas_abertas(
                id_cliente=id_cliente,
                page=page,
                per_page=per_page,
                sortname=sortname,
                sortorder=sortorder,
            )

            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Cliente sem faturas."
                )

            faturas_abertas = res["registros"]

            faturas_abertas_formatadas: Any = []

            for fatura_aberta in faturas_abertas:
                id_contrato = fatura_aberta["id_contrato"]
                contrato_res = await self.financeiro_ixc_cliente.get_contrato(
                    id_contrato=id_contrato
                )
                contrato = (
                    contrato_res["registros"][0]["contrato"]
                    if contrato_res.get("registros")
                    else "N/A"
                )
                faturas_abertas_formatadas.append(
                    {
                        "id": fatura_aberta["id"],
                        "id_contrato": fatura_aberta["id_contrato"],
                        "data_vencimento": fatura_aberta["data_vencimento"],
                        "preco": fatura_aberta["valor"],
                        "contrato": contrato,
                    }
                )

            total = int(res.get("total", 0))

            meta = schemas.Meta(
                total=total,
                page=page,
                per_page=per_page,
            )

            return schemas.FaturaAbertaListOut(
                data=[schemas.FaturaAberta(**f) for f in faturas_abertas_formatadas],
                meta=meta,
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

    async def post_desbloqueio_em_confianca(
        self: Self,
        id_contrato: PositiveInt,
    ) -> schemas.MensagemOut:
        try:
            res = await self.financeiro_ixc_cliente.post_desbloqueio_em_confianca(
                id_contrato=id_contrato
            )
            mensagem = "Nenhuma mensagem retornada."
            mensagem = res.get("message")
            return schemas.MensagemOut(mensagem=mensagem)
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

    async def get_linha_digitavel(
        self: Self, id_fatura: PositiveInt
    ) -> schemas.LinhaDigitavelOut:
        try:
            res = await self.financeiro_ixc_cliente.get_linha_digitavel(
                id_fatura=id_fatura
            )
            reg = res.get("registros")
            if not reg:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sem linha digitável.",
                )
            linha_digitavel = reg[0].get("linha_digitavel")
            if not linha_digitavel:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sem linha digitável.",
                )
            return schemas.LinhaDigitavelOut(
                data=schemas.LinhaDigitavelBase(linha_digitavel=linha_digitavel)
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

    async def get_chave_pix(self: Self, id_fatura: PositiveInt) -> schemas.ChavePixBase:
        try:
            res = await self.financeiro_az7_cliente.get_chave_pix(id_fatura=id_fatura)
            if len(res) < 1 or not res.get("pixCode"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sem chave pix.",
                )
            chave_pix = res.get("pixCode")
            return schemas.ChavePixBase(chave_pix=chave_pix)
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

    async def get_credenciais(
        self: Self, protocolo: Optional[str] = None, cnpj_cpf: Optional[str] = None
    ) -> schemas.CredencialOut:
        try:
            id_cliente = await self.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            res = await self.financeiro_ixc_cliente.get_credenciais(
                id_cliente=id_cliente
            )
            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sem credenciais.",
                )
            cliente = res["registros"][0]
            senha = cliente["senha"]
            hotsite_email = cliente["hotsite_email"]
            return schemas.CredencialOut(usuario=hotsite_email, senha=senha)
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

    async def put_credenciais(
        self: Self,
        id_cliente: PositiveInt,
        credenciais: schemas.CredencialUpdate,
    ) -> schemas.MensagemOut:
        try:
            res = await self.financeiro_ixc_cliente.get_credenciais(
                id_cliente=id_cliente
            )
            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado.",
                )
            cliente_antigo = res["registros"][0]
            novas_credenciais = credenciais.model_dump()
            cliente_atualizado: Any = {**cliente_antigo, **novas_credenciais}
            del cliente_atualizado["id"]
            res = await self.financeiro_ixc_cliente.put_clientes(
                id_cliente=id_cliente, cliente=cliente_atualizado
            )
            mensagem = "Nenhuma mensagem retornada."
            mensagem = res.get("message")
            return schemas.MensagemOut(mensagem=mensagem)
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

    async def get_ultima_fatura_paga(self: Self, id_contrato: PositiveInt) -> Any:
        try:
            res = await self.financeiro_ixc_cliente.get_ultima_fatura_paga(
                id_contrato=id_contrato
            )
            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sem faturas pagas.",
                )
            ultima_fatura_paga = res["registros"][0]

            id = ultima_fatura_paga["id"]
            data_vencimento = ultima_fatura_paga["data_vencimento"]
            preco = ultima_fatura_paga["valor"]
            pagamento_valor = ultima_fatura_paga["pagamento_valor"]
            pagamento_data = ultima_fatura_paga["pagamento_data"]

            return schemas.FaturaPagaBase(
                id=id,
                data_vencimento=data_vencimento,
                preco=preco,
                valor_pago=pagamento_valor,
                data_pagamento=pagamento_data,
            )
        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Validação da resposta falhou: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )
