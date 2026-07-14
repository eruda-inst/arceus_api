from typing import Any
from . import ClienteService
from .. import schemas, clients, utils
from fastapi import HTTPException, status
from pydantic import PositiveInt, NonNegativeInt


class SuporteService:
    @staticmethod
    async def _get_login(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ):
        try:
            # --- Obtém login ---
            endpoint = "radusuarios"
            grid_param = [utils.Param(TB="radusuarios.id", P=id_login)]
            res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Login inexistente."
                )
            login = regs[0]

            return login
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )

    @staticmethod
    async def get_contratos(
        protocolo: str | None,
        cnpj_cpf: str | None,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.ContratoListOut:
        try:
            # --- Obtém contratos ativos ---
            contratos = await ClienteService.get_contratos_ativos(
                protocolo=protocolo,
                cnpj_cpf=cnpj_cpf,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )

            return schemas.ContratoListOut(
                data=[schemas.ContratoOut(**c) for c in contratos],
                meta=schemas.Meta(
                    total_itens=len(contratos),
                    pagina_atual=pagina,
                    itens_por_pagina=itens_por_pagina,
                ),
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )

    @classmethod
    async def get_status_conexao(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ) -> schemas.StatusConexaoOut:
        try:
            # --- Obtém login ---
            login = await cls._get_login(id_login=id_login)

            return schemas.StatusConexaoOut(status_conexao=login["online"])
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )

    @classmethod
    async def get_status_onu(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt | None = None,
        mac_onu: str | None = None,
    ) -> schemas.StatusOnuOut:
        try:
            # Justificativa desta abordagem: O IXC é quebrado
            query_value = None

            # Mac é prioridade, pois o custo computacional é menor (uma requisição a menos)
            if mac_onu:
                query_value = mac_onu
            elif id_login:
                # --- Obtém login ---
                login = await cls._get_login(id_login=id_login)

                query_value = login["onu_mac"]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Informe id_login ou mac_onu.",
                )

            # --- Obtém ONU pelo MAC ---
            endpoint = "radpop_radio_cliente_fibra"
            grid_param = [
                utils.Param(TB="radpop_radio_cliente_fibra.mac", P=query_value)
            ]
            res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="ONU inexistente."
                )
            onu = regs[0]

            # Sinal rx
            sinal_rx = onu.get("sinal_rx")
            if not sinal_rx:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sinal ONU inexistente.",
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
    async def post_desconectar_cliente(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ) -> schemas.MensagemOut:
        try:
            # --- Realiza desconexão de cliente ---
            payload = {"id": id_login}
            endpoint = "desconectar_clientes"
            res = await clients.IxcCliente.post(endpoint=endpoint, payload=payload)
            type = res["msg"][0]["type"]
            if type == "error":
                msgs = res.get("msg", [])
                msg = msgs[0].get("message", "Desconexão malsucedida.")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=utils.Formatter.sanitize(string=msg),
                )

            return schemas.MensagemOut(mensagem="Desconexão bem-sucedida.")
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )

    @staticmethod
    async def get_atendimentos(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.AtendimentoListOut:
        try:
            # --- Obtém atendimentos abertos ---
            endpoint = "su_ticket"
            grid_param = [
                utils.Param(TB="su_ticket.id_login", P=id_login),
                utils.Param(TB="su_ticket.su_status", OP="!=", P="S"),
                utils.Param(TB="su_ticket.su_status", OP="!=", P="C"),
            ]
            res = await clients.IxcCliente.get(
                endpoint=endpoint,
                grid_param=grid_param,
                pagina=pagina,
                itens_por_pagina=itens_por_pagina,
            )
            regs = res.get("registros", [])
            total = res.get("total", 0)
            atendimentos = regs

            atendimentos_parciais: list[schemas.AtendimentoOut] = []

            # Iteração entre atendimentos
            for atendimento in atendimentos:
                # Data criação
                datetime_criacao = atendimento["data_criacao"]
                data_criacao = datetime_criacao.split(" ")[0]

                # Atendimentos parciais
                atendimentos_parciais.append(
                    schemas.AtendimentoOut(
                        id=atendimento["id"],
                        id_assunto=atendimento["id_assunto"],
                        status=atendimento["su_status"],
                        mensagem=atendimento["menssagem"],
                        titulo=atendimento["titulo"],
                        data_criacao=data_criacao,
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
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )

    @staticmethod
    async def post_atendimentos(
        atendimento: schemas.AtendimentoIn,
    ) -> schemas.AtendimentoOut:
        try:
            # --- Cria atendimento ---
            endpoint = "su_ticket"
            payload = atendimento.model_dump()
            menssagem = payload["mensagem"]
            del payload["mensagem"]
            payload["menssagem"] = menssagem
            res = await clients.IxcCliente.post(endpoint=endpoint, payload=payload)
            id = res.get("id")
            if not id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Cadastro malsucedido.",
                )

            # --- Obtém atendimento criado ---
            grid_param = [utils.Param(TB="su_ticket.id", P=id)]
            res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            atendimento_criado: dict[str, Any] = regs[0]

            # Data criação
            datetime_criacao = atendimento_criado["data_criacao"]
            data_criacao = datetime_criacao.split(" ")[0]

            return schemas.AtendimentoOut(
                id=atendimento_criado["id"],
                data_criacao=data_criacao,
                id_assunto=atendimento_criado["id_assunto"],
                status=atendimento_criado["su_status"],
                mensagem=atendimento_criado["menssagem"],
                titulo=atendimento_criado["titulo"],
            )
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )

    @classmethod
    async def put_ip(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
        ip: str | None,
        pool_radius: str | None,
    ) -> schemas.IpOut:
        try:
            # --- Obtém login atual ---
            login_antigo = await cls._get_login(id_login=id_login)

            # Login atualizado
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
            res = await clients.IxcCliente.put(
                endpoint=endpoint, id=id, payload=payload
            )
            type = res["type"]
            if type == "error":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Atualização malsucedida.",
                )

            return schemas.IpOut(ip=novo_ip, pool_radius=int(novo_radius))
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )

    @staticmethod
    async def post_limpar_mac(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ) -> schemas.MensagemOut:
        try:
            # --- Realiza limpeza de MAC ---
            endpoint = "radusuarios_25452"
            payload = {"get_id": id_login}
            res = await clients.IxcCliente.post(endpoint=endpoint, payload=payload)
            type = res["type"]
            if type == "error":
                msg = res.get("message", "Limpeza malsucedida.")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=utils.Formatter.sanitize(string=msg),
                )

            return schemas.MensagemOut(mensagem="Limpeza bem-sucedida.")
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido",
            )

    @classmethod
    async def get_dados_wifi(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ) -> schemas.WifiOut:
        try:
            # --- Obtém login ---
            login = await cls._get_login(id_login=id_login)

            return schemas.WifiOut(
                ssid_wifi_2g=login["ssid_router_wifi"],
                senha_wifi_2g=login["senha_rede_sem_fio"],
                ssid_wifi_5g=login["ssid_router_wifi_5ghz"],
                senha_wifi_5g=login["senha_rede_sem_fio_5ghz"],
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno desconhecido.",
            )
