from typing import Any
from . import service_service
from pydantic import PositiveInt
from fastapi import HTTPException, status
from .. import schemas, clients, services


class SuporteService(service_service.Service):
    @classmethod
    async def get_contratos(
        cls,
        protocolo: str | None,
        cnpj_cpf: str | None,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.ContratoListOut:
        try:
            # --- Cliente ---
            id_cliente = await cls.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )
            res = await clients.IXCCliente.get_cliente_ixc(id=id_cliente)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente não encontrado.",
                )
            cliente = regs[0]

            # --- Contratos ---
            endpoint = "cliente_contrato"
            grid_param = [
                {"TB": "cliente_contrato.id_cliente", "OP": "=", "P": str(id_cliente)},
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "I"},
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "N"},
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "D"},
            ]
            res = await clients.IXCCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Contrato não encontrado.",
                )
            total = res.get("total", 0)
            contratos = regs

            contratos_parciais: list[schemas.Contrato] = []

            # --- Iteração entre contratos ---
            for contrato in contratos:
                id_contrato = contrato.get("id")

                # --- Fatura referência ---
                fatura_referencia: dict[str, Any] | None = (
                    await services.FinanceiroService.get_fatura_referencia(
                        id_contrato=id_contrato
                    )
                )

                if not fatura_referencia:
                    fatura_referencia = {"valor": 0.00, "data_vencimento": ""}

                # --- Login ---
                endpoint = "radusuarios"
                grid_param = [
                    {"TB": "radusuarios.id_contrato", "OP": "=", "P": str(id_contrato)}
                ]
                res = await clients.IXCCliente.get(
                    endpoint=endpoint, grid_param=grid_param
                )
                regs = res.get("registros", [])
                if not regs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Login não encontrado.",
                    )
                login = regs[0]

                # --- Contrato parcial ---
                contratos_parciais.append(
                    schemas.Contrato(
                        id=id_contrato,
                        id_login=login["id"],
                        id_cliente=contrato["id_cliente"],
                        nome_cliente=cliente["razao"],
                        status=contrato["status"],
                        contrato=contrato["contrato"],
                        valor=fatura_referencia["valor"],
                        data_vencimento=fatura_referencia["data_vencimento"],
                        mac_onu=login["onu_mac"],
                    )
                )

            return schemas.ContratoListOut(
                data=contratos_parciais,
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
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    @staticmethod
    async def get_status_conexao(id_login: PositiveInt) -> schemas.StatusConexaoOut:
        try:
            # --- Login ---
            endpoint = "radusuarios"
            grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Login não encontrado.",
                )
            login = regs[0]

            return schemas.StatusConexaoOut(status_conexao=login["online"])
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    # Isto precisa ser limpo?
    @staticmethod
    async def get_status_onu(
        id_login: PositiveInt | None = None, mac_onu: str | None = None
    ) -> schemas.StatusOnuOut:
        if not id_login and not mac_onu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="É necessário informar id_login ou mac_onu.",
            )
        try:
            if id_login is not None:
                try:
                    query_field = "id_login" if id_login else "mac"
                    query_value = id_login if id_login else mac_onu
                    grid_param = [
                        {
                            "TB": f"radpop_radio_cliente_fibra.{query_field}",
                            "OP": "=",
                            "P": str(query_value),
                        }
                    ]
                    endpoint = "radpop_radio_cliente_fibra"
                    res = await clients.IXCCliente.get(
                        endpoint=endpoint, grid_param=grid_param
                    )
                    registros = res.get("registros", [])
                    if registros and "sinal_rx" in registros[0]:
                        codigo = registros[0].get("sinal_rx")
                        if not codigo:
                            return schemas.StatusOnuOut(
                                status_onu=registros[0].get("sinal_rx")
                            )

                        return schemas.StatusOnuOut(
                            status_onu=registros[0].get("sinal_rx")
                        )
                except HTTPException:
                    if not mac_onu:
                        raise
            if mac_onu is not None:
                grid_param = [
                    {
                        "TB": "radpop_radio_cliente_fibra.mac",
                        "OP": "=",
                        "P": str(mac_onu),
                    }
                ]
                endpoint = "radpop_radio_cliente_fibra"
                res = await clients.IXCCliente.get(
                    endpoint=endpoint, grid_param=grid_param
                )
                registros = res.get("registros", [])
                if registros and "sinal_rx" in registros[0]:
                    codigo = registros[0].get("sinal_rx")
                    if not codigo:
                        return schemas.StatusOnuOut(
                            status_onu=registros[0].get("sinal_rx")
                        )

                    return schemas.StatusOnuOut(status_onu=registros[0].get("sinal_rx"))
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="ONU não encontrada."
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    @staticmethod
    async def post_desconectar_cliente(id_login: PositiveInt) -> schemas.MensagemOut:
        try:
            # --- Desconectar cliente ---
            payload = {"id": id_login}
            endpoint = "desconectar_clientes"
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)
            msgs = res.get("msg", [])
            if not msgs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Mensagem não encontrada.",
                )
            msg = msgs[0]

            return schemas.MensagemOut(mensagem=msg["message"])
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    @staticmethod
    async def get_atendimentos(
        id_login: PositiveInt,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.AtendimentoOut:
        try:
            # --- Atendimentos ---
            endpoint = "su_ticket"
            grid_param = [
                {"TB": "su_ticket.id_login", "OP": "=", "P": str(id_login)},
                {"TB": "su_ticket.su_status", "OP": "!=", "P": "S"},
                {"TB": "su_ticket.su_status", "OP": "!=", "P": "C"},
            ]
            res = await clients.IXCCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sem atendimentos abertos.",
                )
            total = res.get("total", 0)
            atendimentos = regs

            atendimentos_parciais: list[schemas.Atendimento] = []

            # --- Iteração entre atendimentos ---
            for atendimento in atendimentos:
                # --- Atendimentos parciais ---
                atendimentos_parciais.append(
                    schemas.Atendimento(
                        id=atendimento["id"],
                        id_assunto=atendimento["id_assunto"],
                        status=atendimento["su_status"],
                        mensagem=atendimento["menssagem"],
                        titulo=atendimento["titulo"],
                        data_criacao=atendimento["data_criacao"],
                    )
                )

            return schemas.AtendimentoOut(
                data=atendimentos_parciais,
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
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    @staticmethod
    async def post_atendimentos(
        atendimento: schemas.AtendimentoIn,
    ) -> schemas.AtendimentoCreate:
        try:
            # --- Atendimento ---
            endpoint = "su_ticket"
            payload = atendimento.model_dump()
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)
            data = res.get("data", None)

            return schemas.AtendimentoCreate(id=data["id"])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    @staticmethod
    async def put_ip(
        id_login: PositiveInt, ip: str | None, pool_radius: str | None
    ) -> schemas.MensagemOut:
        try:
            # --- Login ---
            endpoint = "radusuarios"
            grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Login não encontrado.",
                )
            login_antigo = regs[0]

            # --- Login atualizado ---
            novo_ip = ip if ip else login_antigo["ip"]
            novo_radius = pool_radius if pool_radius else login_antigo["pool_radius"]
            login_atualizado: Any = {
                **login_antigo,
                "ip": novo_ip,
                "pool_radius": novo_radius,
            }
            del login_atualizado["id"]

            # --- Atualiza login ---
            endpoint = "radusuarios"
            id = id_login
            payload = login_atualizado
            res = await clients.IXCCliente.put(
                endpoint=endpoint, id=id, payload=payload
            )
            msg = res.get("message", "Nenhuma mensagem retornada.")

            return schemas.MensagemOut(mensagem=msg)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {e}",
            )

    @staticmethod
    async def post_limpar_mac(id_login: PositiveInt) -> schemas.MensagemOut:
        try:
            # --- Limpar MAC ---
            endpoint = "radusuarios_25452"
            payload = {"get_id": id_login}
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)

            mensagem = res.get("message", "Nenhuma mensagem retornada.")

            return schemas.MensagemOut(mensagem=mensagem)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {e}",
            )

    @staticmethod
    async def get_dados_wifi(id_login: PositiveInt) -> schemas.WifiOut:
        try:
            # --- Login ---
            endpoint = "radusuarios"
            grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Login não encontrado.",
                )
            login = regs[0]

            return schemas.WifiOut(
                ssid_wifi_2g=login["ssid_router_wifi"],
                senha_wifi_2g=login["senha_rede_sem_fio"],
                ssid_wifi_5g=login["ssid_router_wifi_5ghz"],
                senha_wifi_5g=login["senha_rede_sem_fio_5ghz"],
            )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao processar solicitação.",
            )
