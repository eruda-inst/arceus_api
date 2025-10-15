from . import service
from datetime import datetime
from typing import Self, Optional
from .. import utils, schemas, clients
from fastapi import HTTPException, status
from pydantic import ValidationError, PositiveInt


class SuporteService(service.Service):
    """
    Serviço para encapsular a lógica de negócios relacionada às operações de suporte.
    """

    def __init__(self: Self) -> None:
        """
        Inicializa o serviço de suporte e o cliente IXC correspondente.
        """
        super().__init__()
        self.suporte_ixc_cliente = clients.SuporteIXCCliente()

    async def get_contratos(
        self: Self,
        protocolo: str,
        page: Optional[PositiveInt] = 1,
        per_page: Optional[PositiveInt] = 10,
        sortname: Optional[str] = "cliente_contrato.id",
        sortorder: Optional[utils.SortOrder] = utils.SortOrder.ASC,
        db=None,
    ) -> schemas.SuporteContratoListOut:
        """
        Obtém uma lista paginada de contratos de suporte para um cliente.

        Enriquece os dados do contrato com informações de login, MAC da ONU e
        detalhes da próxima fatura a vencer.

        Args:
            protocolo: O protocolo de serviço para identificar o cliente.
            page: O número da página para paginação.
            per_page: O número de itens por página.
            sortname: O campo para ordenação.
            sortorder: A ordem de ordenação.

        Returns:
            Uma lista paginada e formatada de contratos de suporte.

        Raises:
            HTTPException: Se o cliente ou os contratos não forem encontrados, ou em caso de erro.
        """
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
            total = int(contratos_ativos_res.get("total", 0))
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
            base_url = f"/api/v1/suporte/contratos?protocolo={protocolo}"
            links = utils.make_links(
                base_url=base_url, page=page, per_page=per_page, total=total
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
        self: Self, id_login: PositiveInt, db=None
    ) -> schemas.StatusConexaoOut:
        """
        Obtém e rotula o status de conexão de um cliente.

        Args:
            id_login: O ID de login do cliente no IXC.

        Returns:
            O status de conexão rotulado.

        Raises:
            HTTPException: Se o status não for encontrado ou ocorrer um erro.
        """
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
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    async def get_status_onu(
        self: Self,
        id_login: Optional[PositiveInt] = None,
        mac_onu: Optional[str] = None,
        db=None,
    ) -> schemas.StatusONUOut:
        """
        Obtém e rotula o status do sinal da ONU de um cliente.

        A busca pode ser feita pelo ID de login ou pelo MAC da ONU. Há uma tentativa
        de fallback do ID de login para o MAC, se o primeiro falhar.

        Args:
            id_login: O ID de login do cliente (opcional).
            mac_onu: O endereço MAC da ONU (opcional).

        Returns:
            O status do sinal da ONU rotulado.

        Raises:
            HTTPException: Se nenhum parâmetro for fornecido, a ONU não for encontrada,
                           ou ocorrer um erro.
        """
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
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    async def post_desconectar_cliente(
        self: Self, id_login: PositiveInt, db=None
    ) -> schemas.MensagemOut:
        """
        Envia um comando para desconectar um cliente da rede.

        Args:
            id_login: O ID de login do cliente a ser desconectado.

        Returns:
            Uma mensagem de confirmação da ação.

        Raises:
            HTTPException: Se a ação falhar ou ocorrer um erro.
        """
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
        db=None,
    ) -> schemas.AtendimentoOut:
        """
        Obtém uma lista paginada de atendimentos de suporte em aberto.

        Args:
            id_login: O ID de login do cliente.
            page: O número da página para a paginação.
            per_page: A quantidade de itens por página.
            sortname: O campo para ordenação.
            sortorder: A ordem de ordenação.

        Returns:
            Uma lista paginada e formatada de atendimentos.

        Raises:
            HTTPException: Se não houver atendimentos ou ocorrer um erro.
        """
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
            total = int(res.get("total", 0))
            meta = schemas.Meta(total=total, page=page, per_page=per_page)
            base_url = f"/api/v1/suporte/atendimentos?id_login={id_login}"
            links = utils.make_links(
                base_url=base_url, page=page, per_page=per_page, total=total
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
        self: Self, atendimento: schemas.AtendimentoIn, db=None
    ) -> schemas.AtendimentoCreate:
        """
        Cria um novo ticket de atendimento de suporte.

        Args:
            atendimento: Os dados do atendimento a ser criado.

        Returns:
            O ID do atendimento recém-criado.

        Raises:
            HTTPException: Se a criação falhar ou ocorrer um erro.
        """
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
        self: Self, id_login: PositiveInt, ip: schemas.IPUpdate, db=None
    ) -> schemas.MensagemOut:
        """
        Atualiza o endereço IP de um login de cliente.

        Args:
            id_login: O ID do login a ser atualizado.
            ip: Os novos dados de IP a serem aplicados.

        Returns:
            Uma mensagem de confirmação da atualização.

        Raises:
            HTTPException: Se o login não for encontrado ou ocorrer um erro.
        """
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

    async def post_limpar_mac(
        self: Self, id_login: PositiveInt, db=None
    ) -> schemas.MensagemOut:
        """
        Executa a rotina de limpar o endereço MAC de um login.

        Args:
            id_login: O ID do login para o qual o MAC será limpo.

        Returns:
            Uma mensagem de confirmação da ação.

        Raises:
            HTTPException: Se a ação falhar ou ocorrer um erro.
        """
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
