from typing import Any
from . import service_service
from datetime import datetime
from .. import utils, schemas, clients
from fastapi import HTTPException, status
from pydantic import ValidationError, PositiveInt


class SuporteService(service_service.Service):
    @classmethod
    async def get_contratos(
        cls,
        protocolo: str | None = None,
        cnpj_cpf: str | None = None,
        page: PositiveInt | None = 1,
        per_page: PositiveInt | None = 10,
        sortname: str | None = "cliente_contrato.id",
        sortorder: utils.SortOrder | None = utils.SortOrder.ASC,
    ) -> schemas.SuporteContratoListOut:
        try:
            id_cliente = await cls.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            cliente = await clients.SuporteIXCCliente.get_cliente_ixc(id=id_cliente)

            contratos_ativos_res = await clients.SuporteIXCCliente.get_contratos(
                id_cliente=id_cliente,
                page=page,
                per_page=per_page,
                sortname=sortname,
                sortorder=sortorder,
            )
            contratos_ativos = contratos_ativos_res.get("registros", [])
            total = int(contratos_ativos_res.get("total", 0))
            if total < 1:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Nenhum contrato ativo encontrado.",
                )

            for contrato in contratos_ativos:
                a_receber_res = (
                    await clients.SuporteIXCCliente.get_valor_e_data_vencimento(
                        id_contrato=contrato.get("id")
                    )
                )
                id_login_res = await clients.SuporteIXCCliente.get_id_login(
                    id_contrato=contrato.get("id")
                )
                if not id_login_res.get("registros", []):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Sem ID login.",
                    )
                id_login = id_login_res.get("registros")[0]["id"]
                onu_mac_res = await clients.SuporteIXCCliente.get_onu_mac(
                    id_login=id_login
                )

                onu_mac = onu_mac_res["registros"][0]["onu_mac"]
                a_receber = a_receber_res.get("registros", [])

                contrato["id_login"] = id_login
                contrato["mac_onu"] = onu_mac
                titulos_nao_quitados = [r for r in a_receber if r.get("status") != "Q"]

                if not titulos_nao_quitados:
                    contrato["valor"] = 0.00
                    contrato["data_vencimento"] = ""
                    contrato["status"] = utils.rotular_status_contrato(
                        status_contrato_codigo=contrato["status"],
                    )
                    continue

                hoje = datetime.now().date()
                proximo_vencimento = None
                menor_diferenca = None

                for titulo in titulos_nao_quitados:
                    data_vencimento_str = titulo.get("data_vencimento")
                    if data_vencimento_str:
                        try:
                            data_vencimento = datetime.strptime(
                                data_vencimento_str,
                                "%Y-%m-%d",
                            ).date()
                            diferenca = (data_vencimento - hoje).days

                            if diferenca >= 0:
                                if (
                                    menor_diferenca is None
                                    or diferenca < menor_diferenca
                                ):
                                    menor_diferenca = diferenca
                                    proximo_vencimento = titulo
                        except ValueError:
                            continue

                if proximo_vencimento:
                    contrato["valor"] = proximo_vencimento.get("valor")
                    contrato["data_vencimento"] = proximo_vencimento.get(
                        "data_vencimento"
                    )
                else:
                    ultimo_titulo = max(
                        titulos_nao_quitados,
                        key=lambda x: datetime.strptime(
                            x.get("data_vencimento"), "%Y-%m-%d"
                        ).date(),
                    )
                    contrato["valor"] = ultimo_titulo.get("valor")
                    contrato["data_vencimento"] = ultimo_titulo.get("data_vencimento")

                contrato["status"] = utils.rotular_status_contrato(contrato["status"])

                contrato["nome_cliente"] = cliente["registros"][0]["razao"]

            meta = schemas.Meta(total=total, page=page, per_page=per_page)
            return schemas.SuporteContratoListOut(
                data=[schemas.SuporteContrato(**c) for c in contratos_ativos],
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

    @staticmethod
    async def get_status_conexao(id_login: PositiveInt) -> schemas.StatusConexaoOut:
        try:
            res = await clients.SuporteIXCCliente.get_status_conexao(
                id_login=id_login,
            )
            registros = res.get("registros", [])
            if not registros:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum registro."
                )
            codigo = registros[0].get("online")
            rotulo = utils.rotular_status_conexao(
                status_conexao_codigo=codigo,
            )
            return schemas.StatusConexaoOut(
                data=schemas.StatusConexao(status_conexao=rotulo)
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

    @staticmethod
    async def get_status_onu(
        id_login: PositiveInt | None = None, mac_onu: str | None = None
    ) -> schemas.StatusONUOut:
        if not id_login and not mac_onu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="É necessário informar id_login ou mac_onu.",
            )
        try:
            if id_login is not None:
                try:
                    res = await clients.SuporteIXCCliente.get_status_onu(
                        id_login=id_login
                    )
                    registros = res.get("registros", [])
                    if registros and "sinal_rx" in registros[0]:
                        codigo = registros[0].get("sinal_rx")
                        if not codigo:
                            return schemas.StatusONUOut(
                                data=schemas.StatusONU(
                                    status_onu=utils.StatusONURot.SEM_ONU
                                )
                            )
                        rotulo = utils.rotular_status_onu(sinal_rx=float(codigo))
                        return schemas.StatusONUOut(
                            data=schemas.StatusONU(status_onu=rotulo)
                        )
                except HTTPException:
                    if not mac_onu:
                        raise
            if mac_onu is not None:
                res = await clients.SuporteIXCCliente.get_status_onu(mac_onu=mac_onu)
                registros = res.get("registros", [])
                if registros and "sinal_rx" in registros[0]:
                    codigo = registros[0].get("sinal_rx")
                    if not codigo:
                        return schemas.StatusONUOut(
                            data=schemas.StatusONU(
                                status_onu=utils.StatusONURot.SEM_ONU
                            )
                        )
                    rotulo = utils.rotular_status_onu(sinal_rx=float(codigo))
                    return schemas.StatusONUOut(
                        data=schemas.StatusONU(status_onu=rotulo)
                    )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="ONU não encontrada."
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

    @staticmethod
    async def post_desconectar_cliente(id_login: PositiveInt) -> schemas.MensagemOut:
        try:
            res = await clients.SuporteIXCCliente.post_desconectar_cliente(
                id_login=id_login
            )
            mensagem = "Nenhuma mensagem retornada."
            mensagem = res.get("msg")[0]["message"]
            return schemas.MensagemOut(mensagem=mensagem)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    @staticmethod
    async def get_atendimentos(
        id_login: PositiveInt,
        page: PositiveInt | None = 1,
        per_page: PositiveInt | None = 10,
        sortname: str | None = "su_ticket.id",
        sortorder: utils.SortOrder | None = utils.SortOrder.ASC,
    ) -> schemas.AtendimentoOut:
        try:
            res = await clients.SuporteIXCCliente.get_atendimentos(
                id_login=id_login,
                page=page,
                per_page=per_page,
                sortname=sortname,
                sortorder=sortorder,
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

    @staticmethod
    async def post_atendimentos(
        atendimento: schemas.AtendimentoIn,
    ) -> schemas.AtendimentoCreate:
        try:
            res = await clients.SuporteIXCCliente.post_atendimentos(
                atendimento=atendimento
            )
            id_atendimento = res.get("id", None)
            return schemas.AtendimentoCreate(id=int(id_atendimento))
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

    @staticmethod
    async def put_ip(
        id_login: PositiveInt,
        ip: str | None = "",
        pool_radius: str | None = "",
    ) -> schemas.MensagemOut:
        try:
            res = await clients.SuporteIXCCliente.get_login(id_login=id_login)
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
            res = await clients.SuporteIXCCliente.put_ip(
                id_login=id_login, ip=login_atualizado
            )
            mensagem = "Nenhuma mensagem retornada."
            mensagem = res["message"]
            return schemas.MensagemOut(mensagem=mensagem)
        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Erro de validação: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {str(e)}",
            )

    @staticmethod
    async def post_limpar_mac(id_login: PositiveInt) -> schemas.MensagemOut:
        try:
            res = await clients.SuporteIXCCliente.post_limpar_mac(id_login=id_login)
            mensagem = "Nenhuma mensagem retornada."
            mensagem = res.get("message")
            return schemas.MensagemOut(mensagem=mensagem)
        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Erro de validação: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {str(e)}",
            )

    @staticmethod
    async def get_dados_wifi(id_login: PositiveInt) -> schemas.WifiOut:
        try:
            res = await clients.SuporteIXCCliente.get_dados_wifi(id_login=id_login)

            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Dados não encontrados.",
                )

            ssid_wifi_2g = res.get("registros")[0].get("ssid_router_wifi")
            senha_wifi_2g = res.get("registros")[0].get("senha_rede_sem_fio")
            ssid_wifi_5g = res.get("registros")[0].get("ssid_router_wifi_5ghz")
            senha_wifi_5g = res.get("registros")[0].get("senha_rede_sem_fio_5ghz")

            return schemas.WifiOut(
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
