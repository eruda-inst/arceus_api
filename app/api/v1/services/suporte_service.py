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
                    detail="Cliente inexistente.",
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
            total = res.get("total", 0)
            contratos = regs

            contratos_parciais: list[schemas.ContratoOut] = []

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
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Fatura referência inexistente.",
                    )

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
                        detail="Login inexistente.",
                    )
                login = regs[0]

                # --- Contrato parcial ---
                contratos_parciais.append(
                    schemas.ContratoOut(
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
                detail=f"Erro interno desconhecido: {e}",
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
                    status_code=status.HTTP_404_NOT_FOUND, detail="Login inexistente."
                )
            login = regs[0]

            return schemas.StatusConexaoOut(status_conexao=login["online"])
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def get_status_onu(
        id_login: PositiveInt | None = None, mac_onu: str | None = None
    ) -> schemas.StatusOnuOut:
        try:
            query_param = None
            query_value = None

            if id_login:
                query_param = "id_login"
                query_value = id_login
            elif mac_onu:
                query_param = "mac"
                query_value = mac_onu
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Informe id_login ou mac_onu.",
                )

            # --- ONU ---
            endpoint = "radpop_radio_cliente_fibra"
            grid_param = [
                {
                    "TB": f"radpop_radio_cliente_fibra.{query_param}",
                    "OP": "=",
                    "P": str(query_value),
                }
            ]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            onu = regs[0]
            sinal_rx = onu["sinal_rx"]
            if not regs or not sinal_rx:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="ONU inexistente."
                )

            return schemas.StatusOnuOut(status_onu=sinal_rx)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def post_desconectar_cliente(id_login: PositiveInt) -> schemas.MensagemOut:
        try:
            # --- Desconectar cliente ---
            payload = {"id": id_login}
            endpoint = "desconectar_clientes"
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)
            type = res["msgs"][0]["type"]
            if type == "error":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Desconexão malsucedida.",
                )

            return schemas.MensagemOut(mensagem="Desconexão bem-sucedida.")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def get_atendimentos(
        id_login: PositiveInt,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.AtendimentoListOut:
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
            total = res.get("total", 0)
            atendimentos = regs

            atendimentos_parciais: list[schemas.AtendimentoOut] = []

            # --- Iteração entre atendimentos ---
            for atendimento in atendimentos:
                # --- Atendimentos parciais ---
                atendimentos_parciais.append(
                    schemas.AtendimentoOut(
                        id=atendimento["id"],
                        id_assunto=atendimento["id_assunto"],
                        status=atendimento["su_status"],
                        mensagem=atendimento["menssagem"],
                        titulo=atendimento["titulo"],
                        data_criacao=atendimento["data_criacao"],
                    )
                )

            return schemas.AtendimentoListOut(
                data=atendimentos_parciais,
                meta=schemas.Meta(
                    total_itens=total,
                    pagina_atual=pagina,
                    itens_por_pagina=itens_por_pagina,
                ),
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def post_atendimentos(
        atendimento: schemas.AtendimentoIn,
    ) -> schemas.AtendimentoOut:
        try:
            # --- Atendimento ---
            endpoint = "su_ticket"
            payload = atendimento.model_dump()
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)
            type = res.get("type")
            if type == "error":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Cadastro malsucedido.",
                )
            id = res.get("id")

            # --- Atendimento criado ---
            grid_param = [{"TB": "su_ticket.id", "OP": "=", "P": str(id)}]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            atendimento_criado: dict[str, Any] = regs[0]

            return schemas.AtendimentoOut(
                id=atendimento_criado["id"],
                data_criacao=atendimento_criado["data_criacao"],
                id_assunto=atendimento_criado["id_assunto"],
                status=atendimento_criado["su_status"],
                mensagem=atendimento_criado["menssagem"],
                titulo=atendimento_criado["titulo"],
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def put_ip(
        id_login: PositiveInt, ip: str | None, pool_radius: str | None
    ) -> schemas.IpOut:
        try:
            # --- Login ---
            endpoint = "radusuarios"
            grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Login inexistente.",
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
            type = res.get("type")
            if type == "error":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Atualização malsucedida.",
                )

            return schemas.IpOut(ip=novo_ip, pool_radius=int(novo_radius))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @staticmethod
    async def post_limpar_mac(id_login: PositiveInt) -> schemas.MensagemOut:
        try:
            # --- Limpar MAC ---
            endpoint = "radusuarios_25452"
            payload = {"get_id": id_login}
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)
            type = res["type"]
            if type == "error":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Limpeza malsucedida.",
                )

            return schemas.MensagemOut(mensagem="Limpeza bem-sucedida.")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
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
                    detail="Login inexistente.",
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
                detail="Erro interno desconhecido.",
            )
