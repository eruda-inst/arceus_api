from typing import Any

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt

from .. import clients, schemas, utils
from . import ClienteService


class SuporteService:
    @staticmethod
    async def _get_login(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ) -> dict[str, Any]:
        # --- Obtém login ---
        endpoint = "radusuarios"
        grid_param = [utils.Param(TB="radusuarios.id", P=id_login)]
        res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Login inexistente"
            )
        login = regs[0]

        return login

    @staticmethod
    async def get_contratos(
        protocolo: str | None,
        cnpj_cpf: str | None,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.ContratoListOut:
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

    @classmethod
    async def get_status_conexao(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ) -> schemas.StatusConexaoOut:
        # --- Obtém login ---
        login = await cls._get_login(id_login=id_login)

        return schemas.StatusConexaoOut(status_conexao=login["online"])

    @classmethod
    async def get_status_onu(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt | None = None,
        mac_onu: str | None = None,
    ) -> schemas.StatusOnuOut:
        # Justificativa desta abordagem: O IXC é quebrado
        query_value = None

        # Mac é prioridade, pois o custo computacional é menor (uma requisição a menos)
        if mac_onu is not None:
            query_value = mac_onu
        elif id_login is not None:
            # --- Obtém login ---
            login = await cls._get_login(id_login=id_login)

            query_value = login["onu_mac"]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça id_login ou mac_onu",
            )

        # --- Obtém ONU pelo MAC ---
        endpoint = "radpop_radio_cliente_fibra"
        grid_param = [utils.Param(TB="radpop_radio_cliente_fibra.mac", P=query_value)]
        res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="ONU inexistente"
            )
        onu = regs[0]

        # Sinal rx
        if not (sinal_rx := onu.get("sinal_rx")):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sinal ONU inexistente",
            )

        return schemas.StatusOnuOut(status_onu=sinal_rx)

    @staticmethod
    async def post_desconectar_cliente(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ) -> schemas.MensagemOut:
        # --- Realiza desconexão de cliente ---
        payload = {"id": id_login}
        endpoint = "desconectar_clientes"
        res = await clients.IxcCliente.post(endpoint=endpoint, payload=payload)
        type = res["msg"][0]["type"]
        if type == "error":
            msgs = res.get("msg", [])
            msg = msgs[0].get("message", "Desconexão malsucedida")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=utils.Formatter.sanitize(string=msg),
            )

        return schemas.MensagemOut(mensagem="Desconexão bem-sucedida")

    @staticmethod
    async def get_atendimentos(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.AtendimentoListOut:
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
        atendimentos = res.get("registros", [])
        total = res.get("total", 0)

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

    @staticmethod
    async def post_atendimentos(
        atendimento: schemas.AtendimentoIn,
    ) -> schemas.AtendimentoOut:
        # --- Cria atendimento ---
        endpoint = "su_ticket"
        payload = atendimento.model_dump()
        menssagem = payload["mensagem"]
        del payload["mensagem"]
        payload["menssagem"] = menssagem
        res = await clients.IxcCliente.post(endpoint=endpoint, payload=payload)
        if not (id := res.get("id")):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cadastro malsucedido",
            )

        # --- Obtém atendimento criado ---
        grid_param = [utils.Param(TB="su_ticket.id", P=id)]
        res = await clients.IxcCliente.get(endpoint=endpoint, grid_param=grid_param)
        regs = res.get("registros", [])
        atendimento_criado = regs[0]

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

    @classmethod
    async def put_ip(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
        ip: str | None,
        pool_radius: str | None,
    ) -> schemas.IpOut:
        if ip is None and pool_radius is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça ip ou pool_radius",
            )

        # --- Obtém login atual ---
        login_antigo = await cls._get_login(id_login=id_login)

        # Login atualizado
        novo_ip = ip if ip else login_antigo["ip"]
        novo_radius = pool_radius if pool_radius else login_antigo["pool_radius"]
        login_atualizado: Any = {
            **login_antigo,
            "ip": novo_ip or "",
            "pool_radius": novo_radius or "",
        }
        del login_atualizado["id"]

        # --- Atualiza login ---
        endpoint = "radusuarios"
        id = id_login
        payload = login_atualizado
        res = await clients.IxcCliente.put(endpoint=endpoint, id=id, payload=payload)
        if res["type"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Atualização malsucedida",
            )

        return schemas.IpOut(ip=novo_ip, pool_radius=int(novo_radius))

    @staticmethod
    async def post_limpar_mac(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ) -> schemas.MensagemOut:
        # --- Realiza limpeza de MAC ---
        endpoint = "radusuarios_25452"
        payload = {"get_id": id_login}
        res = await clients.IxcCliente.post(endpoint=endpoint, payload=payload)
        if res["type"] == "error":
            msg = res.get("message", "Limpeza malsucedida")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=utils.Formatter.sanitize(string=msg),
            )

        return schemas.MensagemOut(mensagem="Limpeza bem-sucedida")

    @classmethod
    async def get_dados_wifi(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ) -> schemas.WifiOut:
        # --- Obtém login ---
        login = await cls._get_login(id_login=id_login)

        return schemas.WifiOut(
            ssid_wifi_2g=login["ssid_router_wifi"] or None,
            senha_wifi_2g=login["senha_rede_sem_fio"] or None,
            ssid_wifi_5g=login["ssid_router_wifi_5ghz"] or None,
            senha_wifi_5g=login["senha_rede_sem_fio_5ghz"] or None,
        )
