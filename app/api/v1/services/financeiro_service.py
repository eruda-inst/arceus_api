from typing import Any
from . import service_service
from pydantic import PositiveInt
from .. import clients, schemas, utils
from fastapi import HTTPException, status


class FinanceiroService(service_service.Service):
    @classmethod
    async def get_faturas_abertas(
        cls,
        protocolo: str | None,
        cnpj_cpf: str | None,
        page: PositiveInt | None,
        per_page: PositiveInt | None,
    ) -> schemas.FaturaAbertaListOut:
        try:
            id_cliente = await cls.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            grid_param = [
                {"TB": "fn_areceber.id_cliente", "OP": "=", "P": str(id_cliente)},
                {"TB": "fn_areceber.status", "OP": "=", "P": "A"},
            ]

            res = await clients.IXCCliente.get(
                endpoint="fn_areceber",
                grid_param=grid_param,
                page=page,
                per_page=per_page,
            )

            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Cliente sem faturas."
                )

            faturas_abertas = res["registros"]

            faturas_abertas_formatadas: Any = []

            for fatura_aberta in faturas_abertas:
                id_contrato = fatura_aberta["id_contrato"]
                grid_param = [
                    {"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}
                ]
                endpoint = "cliente_contrato"
                contrato_res = await clients.IXCCliente.get(
                    endpoint=endpoint, grid_param=grid_param
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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    @staticmethod
    async def post_desbloqueio_em_confianca(
        id_contrato: PositiveInt,
    ) -> schemas.MensagemOut:
        try:
            endpoint = "desbloqueio_confianca"
            payload = {"id": id_contrato}
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)
            mensagem = "Nenhuma mensagem retornada."
            mensagem = res.get("message")
            return schemas.MensagemOut(mensagem=mensagem)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    @staticmethod
    async def get_linha_digitavel(id_fatura: PositiveInt) -> schemas.LinhaDigitavelOut:
        try:
            grid_param = [{"TB": "fn_areceber.id", "OP": "=", "P": str(id_fatura)}]
            endpoint = "fn_areceber"
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    @staticmethod
    async def get_chave_pix(id_fatura: PositiveInt) -> schemas.ChavePixBase:
        try:
            res = await clients.SeteAZCliente.get_chave_pix(id_fatura=id_fatura)
            if len(res) < 1 or not res.get("pixCode"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sem chave pix.",
                )
            chave_pix = res.get("pixCode")
            return schemas.ChavePixBase(chave_pix=chave_pix)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    @classmethod
    async def get_credenciais(
        cls, protocolo: str | None = None, cnpj_cpf: str | None = None
    ) -> schemas.CredencialOut:
        try:
            id_cliente = await cls.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id_cliente)}]
            endpoint = "cliente"
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    @staticmethod
    async def put_credenciais(
        id_cliente: PositiveInt, credenciais: schemas.CredencialUpdate
    ) -> schemas.MensagemOut:
        try:
            grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id_cliente)}]
            endpoint = "cliente"
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado.",
                )
            cliente_antigo = res["registros"][0]
            novas_credenciais = credenciais.model_dump()
            cliente_atualizado: Any = {**cliente_antigo, **novas_credenciais}
            del cliente_atualizado["id"]

            endpoint = "cliente"
            res = await clients.IXCCliente.put(
                endpoint=endpoint,
                id=id_cliente,
                payload=cliente_atualizado,
            )
            mensagem = res.get("message", "Nenhuma mensagem retornada.")
            return schemas.MensagemOut(mensagem=mensagem)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    @staticmethod
    async def get_ultima_fatura_paga(id_contrato: PositiveInt) -> Any:
        try:
            grid_param = [
                {"TB": "fn_areceber.id_contrato", "OP": "=", "P": str(id_contrato)},
                {"TB": "fn_areceber.status", "OP": "=", "P": "R"},
            ]
            endpoint = "fn_areceber"
            res = await clients.IXCCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                sort_order=utils.SortOrder.DESC,
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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )
