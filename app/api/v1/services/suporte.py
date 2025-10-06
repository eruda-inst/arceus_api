from . import service
from datetime import datetime
from typing import Self, Optional
from .. import utils, schemas, clients
from fastapi import HTTPException, status
from pydantic import ValidationError, PositiveInt


class SuporteService(service.Service):
    def __init__(self: Self) -> None:
        super().__init__()
        self.suporte_ixc_cliente = clients.SuporteIXCCliente()

    async def get_contratos(
        self: Self,
        protocolo: str,
        page: Optional[PositiveInt] = 1,
        per_page: Optional[PositiveInt] = 10,
        sortname: Optional[str] = "cliente_contrato.id",
        sortorder: Optional[utils.SortOrder] = utils.SortOrder.ASC,
    ) -> schemas.SuporteContratoListOut:
        try:
            id_cliente = await self.get_id_cliente_ixc(protocolo=protocolo)

            contratos_ativos_res = await self.suporte_ixc_cliente.get_contratos(
                id_cliente=id_cliente,
                page=page,
                per_page=per_page,
                sortname=sortname,
                sortorder=sortorder,
            )
            contratos_ativos = contratos_ativos_res.get("registros", [])
            total = len(contratos_ativos)
            if total < 1:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Nenhum contrato ativo encontrado.",
                )

            for contrato in contratos_ativos:
                a_receber_res = (
                    await self.suporte_ixc_cliente.get_valor_e_data_vencimento(
                        id_contrato=contrato.get("id")
                    )
                )
                id_login_res = await self.suporte_ixc_cliente.get_id_login(
                    id_contrato=contrato.get("id")
                )
                if not id_login_res.get("registros", []):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Sem ID login.",
                    )
                id_login = id_login_res.get("registros")[0]["id"]
                onu_mac_res = await self.suporte_ixc_cliente.get_onu_mac(
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

            meta = schemas.Meta(total=total, page=page, per_page=per_page)
            base_url = f"/contratos?protocolo={protocolo}"
            links = schemas.Links(
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
            return schemas.SuporteContratoListOut(
                data=[schemas.SuporteContrato(**c) for c in contratos_ativos],
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

    async def get_status_conexao(
        self: Self, id_login: PositiveInt
    ) -> schemas.StatusConexaoOut:
        try:
            res = await self.suporte_ixc_cliente.get_status_conexao(
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
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    async def get_status_onu(
        self: Self,
        id_login: Optional[PositiveInt] = None,
        mac_onu: Optional[str] = None,
    ) -> schemas.StatusONUOut:
        if not id_login and not mac_onu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="É necessário informar id_login ou mac_onu.",
            )
        try:
            if id_login is not None:
                try:
                    res = await self.suporte_ixc_cliente.get_status_onu(
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
                res = await self.suporte_ixc_cliente.get_status_onu(mac_onu=mac_onu)
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
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    async def post_desconectar_cliente(
        self: Self, id_login: PositiveInt
    ) -> schemas.MensagemOut:
        try:
            res = await self.suporte_ixc_cliente.post_desconectar_cliente(
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

    async def get_atendimentos(
        self: Self,
        id_login: PositiveInt,
        page: Optional[PositiveInt] = 1,
        per_page: Optional[PositiveInt] = 10,
        sortname: Optional[str] = "su_ticket.id",
        sortorder: Optional[utils.SortOrder] = utils.SortOrder.ASC,
    ) -> schemas.AtendimentoOut:
        try:
            res = await self.suporte_ixc_cliente.get_atendimentos(
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
            formatted = []
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
            total = len(registros)
            meta = schemas.Meta(total=total, page=page, per_page=per_page)
            base_url = f"/atendimentos?id_login={id_login}"
            links = schemas.Links(
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
            return schemas.AtendimentoOut(
                data=[schemas.Atendimento(**i) for i in formatted],
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

    async def post_atendimentos(
        self: Self, atendimento: schemas.AtendimentoIn
    ) -> schemas.AtendimentoCreate:
        try:
            res = await self.suporte_ixc_cliente.post_atendimentos(
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

    async def put_ip(
        self: Self, id_login: PositiveInt, ip: schemas.IPUpdate
    ) -> schemas.MensagemOut:
        try:
            res = await self.suporte_ixc_cliente.get_login(id_login=id_login)
            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Login não encontrado.",
                )
            login_antigo = res["registros"][0]
            novo_ip = ip.model_dump()
            login_atualizado = {**login_antigo, **novo_ip}
            del login_atualizado["id"]
            res = await self.suporte_ixc_cliente.put_ip(
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

    async def post_limpar_mac(self: Self, id_login: PositiveInt) -> schemas.MensagemOut:
        try:
            res = await self.suporte_ixc_cliente.post_limpar_mac(id_login=id_login)
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
