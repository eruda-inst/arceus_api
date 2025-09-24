from typing import Self, Optional
from datetime import datetime
from pydantic import ValidationError
from ..clients import SuporteOpaCliente, SuporteIXCCliente
from fastapi import HTTPException, status
from ..utils import (
    rotular_status_contrato,
    rotular_status_atendimento,
    rotular_status_conexao,
    rotular_status_onu,
    SortOrder,
)
from ..schemas import (
    StatusONUOut,
    Atendimento,
    AtendimentoIn,
    AtendimentoOut,
    SuporteContratoListOut,
    SuporteContrato,
    Links,
    Meta,
    LoginIn,
    LoginOut,
    StatusConexao,
    StatusConexaoOut,
    StatusONU,
    AtendimentoCreate,
)


class Service:
    def __init__(self: Self) -> None:
        self.opa_cliente = SuporteOpaCliente()
        self.ixc_cliente = SuporteIXCCliente()

    async def get_contratos_ativos(
        self: Self,
        protocolo: str,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "cliente_contrato.id",
        sortorder: Optional[SortOrder] = SortOrder.ASC,
    ) -> SuporteContratoListOut:
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

            contratos_ativos_res = await self.ixc_cliente.get_contratos_ativos(
                id_cliente=id_cliente_ixc,
                page=page,
                per_page=per_page,
                sortname=sortname,
                sortorder=sortorder,
            )
            contratos_ativos = contratos_ativos_res.get("registros", [])
            total = contratos_ativos.__len__()
            if total < 1:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Nenhum contrato ativo encontrado.",
                )

            for contrato in contratos_ativos:
                a_receber_res = await self.ixc_cliente.get_valor_e_data_vencimento(
                    id_contrato=contrato.get("id")
                )
                id_login_res = await self.ixc_cliente.get_id_login(
                    id_contrato=contrato.get("id")
                )
                if not id_login_res.get("registros", []):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Sem ID login.",
                    )
                id_login = id_login_res.get("registros")[0]["id"]
                onu_mac_res = await self.ixc_cliente.get_onu_mac(id_login=id_login)

                onu_mac = onu_mac_res["registros"][0]["onu_mac"]
                a_receber = a_receber_res.get("registros", [])

                contrato["id_login"] = id_login
                contrato["mac_onu"] = onu_mac
                titulos_nao_quitados = [r for r in a_receber if r.get("status") != "Q"]

                if not titulos_nao_quitados:
                    contrato["valor"] = 0.00
                    contrato["data_vencimento"] = ""
                    contrato["status"] = rotular_status_contrato(
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

                contrato["status"] = rotular_status_contrato(contrato["status"])

            meta = Meta(total=total, page=page, per_page=per_page)
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
            return SuporteContratoListOut(
                data=[SuporteContrato(**c) for c in contratos_ativos],
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

    async def get_status_conexao(self: Self, id_login: int) -> StatusConexaoOut:
        try:
            res = await self.ixc_cliente.get_status_conexao(
                id_login=id_login,
            )
            registros = res.get("registros", [])
            if not registros:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum registro."
                )
            codigo = registros[0].get("online")
            rotulo = rotular_status_conexao(
                status_conexao_codigo=codigo,
            )
            return StatusConexaoOut(data=StatusConexao(status_conexao=rotulo))
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
        self: Self, id_login: Optional[int] = None, mac_onu: Optional[str] = None
    ) -> StatusONUOut:
        if not id_login and not mac_onu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="É necessário informar id_login ou mac_onu.",
            )
        try:
            if id_login is not None:
                try:
                    res = await self.ixc_cliente.get_status_onu(id_login=id_login)
                    registros = res.get("registros", [])
                    if registros and "sinal_rx" in registros[0]:
                        codigo = float(registros[0]["sinal_rx"])
                        rotulo = rotular_status_onu(sinal_rx=codigo)
                        return StatusONUOut(data=StatusONU(status_onu=rotulo))
                except HTTPException:
                    if not mac_onu:
                        raise
            if mac_onu is not None:
                res = await self.ixc_cliente.get_status_onu(mac_onu=mac_onu)
                registros = res.get("registros", [])
                if registros and "sinal_rx" in registros[0]:
                    codigo = float(registros[0]["sinal_rx"])
                    rotulo = rotular_status_onu(sinal_rx=codigo)
                    return StatusONUOut(data=StatusONU(status_onu=rotulo))
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

    async def post_desconectar_cliente(self: Self, id_login: int) -> None:
        try:
            await self.ixc_cliente.post_desconectar_cliente(id_login=id_login)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    async def get_atendimentos_abertos(
        self: Self,
        id_login: int,
        page: Optional[int] = 1,
        per_page: Optional[int] = 10,
        sortname: Optional[str] = "su_ticket.id",
        sortorder: Optional[SortOrder] = SortOrder.ASC,
    ) -> AtendimentoOut:
        try:
            res = await self.ixc_cliente.get_atendimentos_abertos(
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
                        "status": rotular_status_atendimento(
                            status_atendimento_codigo=a.get("su_status"),
                        ),
                        "mensagem": a.get("menssagem") or a.get("mensagem") or "",
                        "titulo": a.get("titulo"),
                        "data_criacao": a.get("data_criacao"),
                    }
                )
            total = registros.__len__()
            meta = Meta(total=total, page=page, per_page=per_page)
            base_url = f"/atendimentos?id_login={id_login}"
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
            return AtendimentoOut(
                data=[Atendimento(**i) for i in formatted], meta=meta, links=links
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
        self: Self, atendimento: AtendimentoIn
    ) -> AtendimentoCreate:
        try:
            res = await self.ixc_cliente.post_atendimentos(atendimento=atendimento)
            id_atendimento = res.get("id", None)
            return AtendimentoCreate(id=int(id_atendimento))
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

    async def patch_logins(self: Self, id: int, login: LoginIn) -> LoginOut:
        try:
            res = await self.ixc_cliente.get_login(id=id)
            if not res.get("registros"):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Login não encontrado.",
                )
            login_antigo = res["registros"][0]

            novo_login = login.model_dump(exclude_unset=True)
            login_atualizado = {**login_antigo, **novo_login}

            del login_atualizado["id"]

            await self.ixc_cliente.put_login(id=id, login=login_atualizado)

            res_atualizado = await self.ixc_cliente.get_login(id=id)
            login_final = res_atualizado["registros"][0]

            return LoginOut(mensagem="Login atualizado com sucesso!")
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
