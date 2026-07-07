import statistics
from . import ClienteService
from typing import Any
from pydantic import PositiveInt
from .. import clients, schemas, utils
from fastapi import HTTPException, status


class FinanceiroService:
    @staticmethod
    async def _get_ultima_fatura_paga(
        id_contrato: PositiveInt,
    ) -> dict[str, Any] | None:
        try:
            # --- Faturas pagas ---
            endpoint = "fn_areceber"
            grid_param = [
                {"TB": "fn_areceber.id_contrato", "OP": "=", "P": str(id_contrato)},
                {"TB": "fn_areceber.status", "OP": "=", "P": "R"},
            ]
            res = await clients.IXCCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                sort_order=utils.SortOrder.DESC,
            )
            regs = res.get("registros", [])
            if not regs:
                return None
            faturas_pagas = regs

            # --- Ultima fatura paga ---
            ultimas_faturas_pagas = faturas_pagas[:3]
            ultima_fatura_paga = ultimas_faturas_pagas[0]

            # --- Valor mais frequente ---
            valores = [float(u["valor"]) for u in ultimas_faturas_pagas]
            valor_mais_frequente = statistics.mode(valores)

            return {
                "id": int(ultima_fatura_paga["id"]),
                "status": ultima_fatura_paga["status"],
                "data_vencimento": ultima_fatura_paga["data_vencimento"],
                "valor": valor_mais_frequente,
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @classmethod
    async def _get_proxima_fatura_aberta(
        cls, id_contrato: PositiveInt
    ) -> dict[str, Any] | None:
        try:
            # --- Faturas abertas ---
            endpoint = "fn_areceber"
            grid_param = [
                {"TB": "fn_areceber.id_contrato", "OP": "=", "P": str(id_contrato)},
                {"TB": "fn_areceber.status", "OP": "!=", "P": "R"},
                {"TB": "fn_areceber.status", "OP": "!=", "P": "C"},
            ]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                return None
            faturas_abertas = regs

            # --- Proxima fatura aberta ---
            proximas_faturas_abertas = faturas_abertas[:3]
            proxima_fatura_aberta = proximas_faturas_abertas[0]

            # --- Valor mais frequente ---
            valores = [float(p["valor"]) for p in proximas_faturas_abertas]
            valor_mais_frequente = statistics.mode(valores)

            return {
                "id": int(proxima_fatura_aberta["id"]),
                "status": proxima_fatura_aberta["status"],
                "data_vencimento": proxima_fatura_aberta["data_vencimento"],
                "valor": valor_mais_frequente,
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @classmethod
    async def get_fatura_referencia(
        cls, id_contrato: PositiveInt
    ) -> dict[str, Any] | None:
        try:
            proxima_fatura_aberta = await cls._get_proxima_fatura_aberta(
                id_contrato=id_contrato
            )

            if proxima_fatura_aberta:
                return proxima_fatura_aberta

            ultima_fatura_paga = await cls._get_ultima_fatura_paga(
                id_contrato=id_contrato
            )

            return ultima_fatura_paga
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def get_faturas_abertas(
        protocolo: str | None,
        cnpj_cpf: str | None,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.FaturaListOut:
        try:
            cliente = await ClienteService.get_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            # --- Faturas Abertas ---
            endpoint = "fn_areceber"
            grid_param = [
                {"TB": "fn_areceber.id_cliente", "OP": "=", "P": str(cliente["id"])},
                {"TB": "fn_areceber.status", "OP": "!=", "P": "R"},
                {"TB": "fn_areceber.status", "OP": "!=", "P": "C"},
            ]
            res = await clients.IXCCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )
            regs = res.get("registros", [])
            faturas_abertas = regs
            total = res.get("total", 0)

            faturas_abertas_parciais: list[schemas.FaturaOut] = []

            # --- Iteração entre faturas abertas ---
            for fatura_aberta in faturas_abertas:
                # --- Contrato ---
                id_contrato = fatura_aberta["id_contrato"]
                endpoint = "cliente_contrato"
                grid_param = [
                    {"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}
                ]
                res = await clients.IXCCliente.get(
                    endpoint=endpoint, grid_param=grid_param
                )
                regs = res.get("registros", [])
                if not regs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Contrato inexistente.",
                    )
                contrato = regs[0]

                # --- Faturas abertas parciais ---
                faturas_abertas_parciais.append(
                    schemas.FaturaOut(
                        id=fatura_aberta["id"],
                        contrato=contrato["contrato"],
                        data_vencimento=fatura_aberta["data_vencimento"],
                        id_contrato=contrato["id"],
                        preco=fatura_aberta["valor"],
                    )
                )

            return schemas.FaturaListOut(
                data=faturas_abertas_parciais,
                meta=schemas.Meta(
                    total_itens=total,
                    pagina_atual=pagina,
                    itens_por_pagina=itens_por_pagina,
                ),
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def post_desbloqueio_em_confianca(
        id_contrato: PositiveInt,
    ) -> schemas.MensagemOut:
        try:
            # --- Desbloqueio de confiança ---
            endpoint = "desbloqueio_confianca"
            payload = {"id": id_contrato}
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)
            type = res["type"]
            if type == "error":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Desbloqueio malsucedido.",
                )

            return schemas.MensagemOut(mensagem="Desbloqueio bem-sucedido.")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def get_linha_digitavel(id_fatura: PositiveInt) -> schemas.LinhaDigitavelOut:
        try:
            # -- Fatura ---
            endpoint = "fn_areceber"
            grid_param = [{"TB": "fn_areceber.id", "OP": "=", "P": str(id_fatura)}]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros")
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Fatura inexistente."
                )
            fatura = regs[0]

            # -- Linha digitável ---
            linha_digitavel = fatura.get("linha_digitavel", None)
            if not linha_digitavel:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Linha digitável inexistente.",
                )

            return schemas.LinhaDigitavelOut(linha_digitavel=linha_digitavel)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def get_chave_pix(id_fatura: PositiveInt) -> schemas.ChavePixOut:
        try:
            # --- Fatura ---
            res = await clients.SeteAZCliente.get_chave_pix(id_fatura=id_fatura)
            fatura = res.get("id")
            if not fatura:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Fatura inexistente."
                )

            # --- Chave pix ---
            chave_pix = res.get("pixCode")
            if not chave_pix:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chave pix inexistente.",
                )

            return schemas.ChavePixOut(chave_pix=chave_pix)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def get_credenciais(
        protocolo: str | None = None, cnpj_cpf: str | None = None
    ) -> schemas.CredencialOut:
        try:
            # --- Cliente ---
            cliente = await ClienteService.get_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            return schemas.CredencialOut(
                usuario=cliente["hotsite_email"], senha=cliente["senha"]
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def put_credenciais(
        id_cliente: PositiveInt, senha: str
    ) -> schemas.CredencialOut:
        try:
            # --- Cliente ---
            endpoint = "cliente"
            grid_param = [{"TB": "cliente.id", "OP": "=", "P": str(id_cliente)}]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Cliente inexistente."
                )
            cliente_antigo = regs[0]

            # --- Cliente atualizado ---
            cliente_atualizado: dict[str, Any] = {**cliente_antigo, "senha": senha}
            del cliente_atualizado["id"]

            # --- Atualiza cliente ---
            id = cliente_antigo["id"]
            res = await clients.IXCCliente.put(
                endpoint=endpoint, id=id, payload=cliente_atualizado
            )
            type = res["type"]
            if type == "error":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Cadastro malsucedido.",
                )

            return schemas.CredencialOut(
                usuario=cliente_atualizado["hotsite_email"], senha=senha
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )
