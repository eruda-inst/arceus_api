from typing import Any
from . import service_service
from pydantic import PositiveInt
from fastapi import HTTPException, status
from .. import utils, schemas, clients, services


class SuporteService(service_service.Service):
    @classmethod
    async def get_contratos(
        cls,
        protocolo: str | None = None,
        cnpj_cpf: str | None = None,
        page: PositiveInt | None = 1,
        per_page: PositiveInt | None = 10,
    ) -> schemas.SuporteContratoListOut:
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
                    detail="Nenum cliente encontrado.",
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
                endpoint=endpoint, grid_param=grid_param, page=page, per_page=per_page
            )
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Nenhum contrato encontrado.",
                )
            total = res.get("total", 0)
            contratos = regs

            contratos_parciais: list[schemas.SuporteContrato] = []

            # --- Iteração entre contratos ---
            for contrato in contratos:
                # --- Pŕoxima fatura aberta ----
                id_contrato = contrato.get("id")

                proxima_fatura_aberta = (
                    await services.FinanceiroService.get_proxima_fatura_aberta(
                        id_contrato=id_contrato
                    )
                )

                if not proxima_fatura_aberta:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Nenhuma fatura aberta encontrada.",
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
                        detail="Nenhum login encontrado.",
                    )
                login = regs[0]

                # --- Contrato parcial ---
                contratos_parciais.append(
                    schemas.SuporteContrato(
                        id=id_contrato,
                        id_login=login.get("id"),
                        id_cliente=contrato.get("id_cliente"),
                        nome_cliente=cliente.get("razao"),
                        status=utils.rotular_status_contrato(
                            status_contrato_codigo=contrato.get("status")
                        ),
                        contrato=contrato.get("contrato"),
                        valor=proxima_fatura_aberta["valor"],
                        data_vencimento=proxima_fatura_aberta["data_vencimento"],
                        mac_onu=login.get("onu_mac"),
                    )
                )

            return schemas.SuporteContratoListOut(
                data=contratos_parciais,
                meta=schemas.Meta(total=total, page=page, per_page=per_page),
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    @staticmethod
    async def get_status_conexao(id_login: PositiveInt) -> schemas.NewStatusConexaoOut:
        try:
            grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
            endpoint = "radusuarios"
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            registros = res.get("registros", [])
            if not registros:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum registro."
                )
            return schemas.NewStatusConexaoOut(
                status_conexao=registros[0].get("online")
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )

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
            payload = {"id": id_login}
            endpoint = "desconectar_clientes"
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)
            mensagem = "Nenhuma mensagem retornada."
            mensagem = res.get("msg")[0]["message"]
            return schemas.MensagemOut(mensagem=mensagem)
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
        page: PositiveInt | None = 1,
        per_page: PositiveInt | None = 10,
    ) -> schemas.AtendimentoOut:
        try:
            endpoint = "su_ticket"
            grid_param = [
                {"TB": "su_ticket.id_login", "OP": "=", "P": str(id_login)},
                {"TB": "su_ticket.su_status", "OP": "!=", "P": "S"},
                {"TB": "su_ticket.su_status", "OP": "!=", "P": "C"},
            ]
            res = await clients.IXCCliente.get(
                endpoint=endpoint, grid_param=grid_param, page=page, per_page=per_page
            )
            registros = res.get("registros", [])
            if not registros:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sem atendimentos abertos.",
                )
            formatted: Any = []
            for a in registros:
                formatted.append(
                    {
                        "id": a.get("id"),
                        "id_assunto": a.get("id_assunto"),
                        "status": utils.rotular_status_atendimento(
                            status_atendimento_codigo=a.get("su_status"),
                        ),
                        "mensagem": a.get("menssagem") or a.get("mensagem") or "",
                        "titulo": a.get("titulo"),
                        "data_criacao": a.get("data_criacao"),
                    }
                )
            total = int(res.get("total", 0))
            meta = schemas.Meta(total=total, page=page, per_page=per_page)

            return schemas.AtendimentoOut(
                data=[schemas.Atendimento(**i) for i in formatted],
                meta=meta,
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
            endpoint = "su_ticket"
            payload = atendimento.model_dump()
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)
            id_atendimento = res.get("id", None)
            return schemas.AtendimentoCreate(id=int(id_atendimento))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    @staticmethod
    async def put_ip(
        id_login: PositiveInt,
        ip: str | None = "",
        pool_radius: str | None = "",
    ) -> schemas.MensagemOut:
        try:
            grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
            endpoint = "radusuarios"

            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Login não encontrado.",
                )
            login_antigo = res["registros"][0]
            novo_ip = ip if ip else login_antigo["ip"]
            novo_radius = pool_radius if pool_radius else login_antigo["pool_radius"]
            login_atualizado: Any = {
                **login_antigo,
                "ip": novo_ip,
                "pool_radius": novo_radius,
            }
            del login_atualizado["id"]

            endpoint = "radusuarios"
            id = id_login
            payload = login_atualizado

            res = await clients.IXCCliente.put(
                endpoint=endpoint, id=id, payload=payload
            )

            mensagem = "Nenhuma mensagem retornada."
            mensagem = res["message"]
            return schemas.MensagemOut(mensagem=mensagem)
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
            endpoint = "radusuarios_25452"
            payload = {"get_id": id_login}
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)
            mensagem = "Nenhuma mensagem retornada."
            mensagem = res.get("message")
            return schemas.MensagemOut(mensagem=mensagem)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {e}",
            )

    @staticmethod
    async def get_dados_wifi(id_login: PositiveInt) -> schemas.NewWifiOut:
        try:
            endpoint = "radusuarios"
            grid_param = [{"TB": "radusuarios.id", "OP": "=", "P": str(id_login)}]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)

            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Dados não encontrados.",
                )

            ssid_wifi_2g = res.get("registros")[0].get("ssid_router_wifi")
            senha_wifi_2g = res.get("registros")[0].get("senha_rede_sem_fio")
            ssid_wifi_5g = res.get("registros")[0].get("ssid_router_wifi_5ghz")
            senha_wifi_5g = res.get("registros")[0].get("senha_rede_sem_fio_5ghz")

            return schemas.NewWifiOut(
                ssid_wifi_2g=ssid_wifi_2g,
                senha_wifi_2g=senha_wifi_2g,
                ssid_wifi_5g=ssid_wifi_5g,
                senha_wifi_5g=senha_wifi_5g,
            )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao processar solicitação.",
            )
