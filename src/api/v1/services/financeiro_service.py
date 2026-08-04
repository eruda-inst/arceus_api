import statistics
from typing import Any

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt

from .. import clients, schemas, services, utils
from . import ClienteService


class FinanceiroService:
    @staticmethod
    async def _get_ultima_fatura_paga(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_contrato: NonNegativeInt,
    ) -> dict[str, Any] | None:
        # --- Obtém faturas pagas ---
        endpoint = "fn_areceber"
        grid_param = [
            utils.Param(TB="fn_areceber.id_contrato", P=id_contrato),
            utils.Param(TB="fn_areceber.status", P="R"),
        ]
        res = await clients.IxcCliente.get(
            endpoint=endpoint,
            grid_param=grid_param,
            sort_order=utils.SortOrder.DESC,
        )
        if not (faturas_pagas := res.get("registros", [])):
            return None

        # Ultima fatura paga
        ultimas_faturas_pagas = faturas_pagas[:3]
        ultima_fatura_paga = ultimas_faturas_pagas[0]

        # Valor da fatura
        valores = [float(u["valor"]) for u in ultimas_faturas_pagas]
        valor = statistics.mode(valores)

        # Dia de vencimento da fatura
        datas_vencimento = [u["data_vencimento"] for u in ultimas_faturas_pagas]
        dias_vencimento = [d.split("-")[2] for d in datas_vencimento]
        dia_vencimento = statistics.mode(dias_vencimento)

        return {
            "id": int(ultima_fatura_paga["id"]),
            "status": ultima_fatura_paga["status"],
            "dia_vencimento_fatura": dia_vencimento,
            "valor": valor,
        }

    @staticmethod
    async def _get_proxima_fatura_aberta(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_contrato: NonNegativeInt,
    ) -> dict[str, Any] | None:
        # --- Obtém faturas abertas ---
        endpoint = "fn_areceber"
        grid_param = [
            utils.Param(TB="fn_areceber.id_contrato", P=id_contrato),
            utils.Param(TB="fn_areceber.status", OP="!=", P="R"),
            utils.Param(TB="fn_areceber.status", OP="!=", P="C"),
        ]
        res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
        if not (faturas_abertas := res.get("registros", [])):
            return None

        # Proxima fatura aberta
        proximas_faturas_abertas = faturas_abertas[:3]
        proxima_fatura_aberta = proximas_faturas_abertas[0]

        # Valor da fatura
        valores = [float(p["valor"]) for p in proximas_faturas_abertas]
        valor = statistics.mode(valores)

        # Dia de vencimento da fatura
        datas_vencimento = [p["data_vencimento"] for p in proximas_faturas_abertas]
        dias_vencimento = [d.split("-")[2] for d in datas_vencimento]
        dia_vencimento = statistics.mode(dias_vencimento)

        return {
            "id": int(proxima_fatura_aberta["id"]),
            "status": proxima_fatura_aberta["status"],
            "dia_vencimento_fatura": dia_vencimento,
            "valor": valor,
        }

    @classmethod
    async def get_fatura_referencia(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_contrato: NonNegativeInt,
    ) -> dict[str, Any] | None:
        proxima_fatura_aberta = await cls._get_proxima_fatura_aberta(
            id_contrato=id_contrato
        )

        if proxima_fatura_aberta:
            return proxima_fatura_aberta

        ultima_fatura_paga = await cls._get_ultima_fatura_paga(id_contrato=id_contrato)

        return ultima_fatura_paga

    @staticmethod
    async def get_faturas_abertas(
        protocolo: str | None,
        cnpj_cpf: str | None,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.ListOut[schemas.FaturaOut]:
        # --- Obtém contratos ativos ---
        contratos = await services.ClienteService.get_contratos_ativos(
            protocolo=protocolo,
            cnpj_cpf=cnpj_cpf,
            pagina=pagina,
            itens_por_pagina=itens_por_pagina,
        )

        faturas_abertas_parciais: list[schemas.FaturaOut] = []

        # Iteração entre contratos
        # Abordagem mais segura (fatura_aberta["id_contrato"] pode ser 0)
        for contrato in contratos:
            id_contrato = contrato["id"]

            # --- Obtém faturas Abertas ---
            endpoint = "fn_areceber"
            grid_param = [
                utils.Param(TB="fn_areceber.id_contrato", P=id_contrato),
                utils.Param(TB="fn_areceber.status", OP="!=", P="R"),
                utils.Param(TB="fn_areceber.status", OP="!=", P="C"),
            ]
            res = await clients.IxcCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )
            faturas_abertas = res.get("registros", [])

            # Iteração entre faturas abertas
            for fatura_aberta in faturas_abertas:
                # Faturas abertas parciais
                faturas_abertas_parciais.append(
                    schemas.FaturaOut(
                        id=fatura_aberta["id"],
                        contrato=contrato["nome_plano"],
                        data_vencimento=fatura_aberta["data_vencimento"],
                        id_contrato=id_contrato,
                        preco=fatura_aberta["valor"],
                    )
                )

        return schemas.ListOut[schemas.FaturaOut](
            data=faturas_abertas_parciais,
            meta=schemas.MetaOut(
                total_itens=len(faturas_abertas_parciais),
                pagina_atual=pagina or 1,
                itens_por_pagina=itens_por_pagina or 10,
            ),
        )

    @staticmethod
    async def post_desbloqueio_em_confianca(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_contrato: NonNegativeInt,
    ) -> schemas.MensagemOut:
        # --- Realiza desbloqueio de confiança ---
        endpoint = "desbloqueio_confianca"
        payload = {"id": id_contrato}
        res = await clients.IxcCliente.post(endpoint=endpoint, payload=payload)
        if res["type"] == "error":
            msg = res.get("message", "Desbloqueio malsucedido")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=utils.Formatter.sanitize(string=msg),
            )

        return schemas.MensagemOut(mensagem="Desbloqueio bem-sucedido")

    @staticmethod
    async def get_linha_digitavel(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_fatura: NonNegativeInt,
    ) -> schemas.LinhaDigitavelOut:
        # --- Obtém fatura ---
        endpoint = "fn_areceber"
        grid_param = [utils.Param(TB="fn_areceber.id", P=id_fatura)]
        res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Fatura inexistente"
            )
        fatura = regs[0]

        # Linha digitável
        if not (linha_digitavel := fatura.get("linha_digitavel")):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Linha digitável inexistente",
            )

        return schemas.LinhaDigitavelOut(linha_digitavel=linha_digitavel)

    @staticmethod
    async def get_chave_pix(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_fatura: NonNegativeInt,
    ) -> schemas.ChavePixOut:
        # --- Obtém fatura ---
        res = await clients.SeteAZCliente.get_fatura(id_fatura=id_fatura)
        if "id" not in res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Fatura inexistente"
            )

        # Chave pix
        if not (chave_pix := res.get("pixCode")):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chave pix inexistente",
            )

        return schemas.ChavePixOut(chave_pix=chave_pix)

    @staticmethod
    async def get_credenciais(
        protocolo: str | None = None, cnpj_cpf: str | None = None
    ) -> schemas.CredencialOut:
        # --- Obtém cliente ---
        cliente = await ClienteService.get_cliente_ixc(
            protocolo=protocolo, cnpj_cpf=cnpj_cpf
        )

        return schemas.CredencialOut(
            usuario=cliente["hotsite_email"], senha=cliente["senha"]
        )

    @staticmethod
    async def put_credenciais(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_cliente: NonNegativeInt,
        senha: str,
    ) -> schemas.CredencialOut:
        # --- Obtém cliente atual ---
        cliente_antigo = await services.ClienteService.get_cliente_ixc(
            id_cliente=id_cliente
        )

        # Cliente atualizado
        cliente_atualizado: dict[str, Any] = {**cliente_antigo, "senha": senha}
        del cliente_atualizado["id"]

        # --- Atualiza cliente ---
        endpoint = "cliente"
        id = cliente_antigo["id"]
        res = await clients.IxcCliente.put(
            endpoint=endpoint, id=id, payload=cliente_atualizado
        )
        if res["type"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cadastro malsucedido",
            )

        return schemas.CredencialOut(
            usuario=cliente_atualizado["hotsite_email"], senha=senha
        )
