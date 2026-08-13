from typing import Any

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt

from .. import clients, schemas, utils
from .client_service import ClientService
from .financeiro_service import FinanceiroService


class SuporteService:
    @staticmethod
    async def _get_login(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ) -> dict[str, Any]:
        # --- Obtém login ---
        endpoint = "radusuarios"
        grid_param = [utils.Param(TB="radusuarios.id", P=id_login)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Login inexistente"
            )
        login = regs[0]

        return login

    @staticmethod
    async def get_contrato(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_contrato: NonNegativeInt,
    ) -> schemas.ContratoOutSchema:
        # --- Obtém contrato ---
        endpoint = "cliente_contrato"
        grid_param = [utils.Param(TB="cliente_contrato.id", P=id_contrato)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contrato inexistente"
            )
        contrato = regs[0]

        # --- Obtém login ---
        endpoint = "radusuarios"
        id_cliente = contrato["id_cliente"]
        grid_param = [utils.Param(TB="radusuarios.id_cliente", P=id_cliente)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        regs = res.get("registros", [])
        login = regs[0] if len(regs) > 0 else {}

        # --- Obtém cliente IXC ---
        cliente = await ClientService.get_cliente_ixc(id_cliente=id_cliente)

        # Nome do cliente
        nome = cliente.get("nome")
        razao = cliente.get("razao")
        nome_cliente = str(nome if nome else razao)

        # Fatura referência
        fatura_referencia: (
            dict[str, Any] | None
        ) = await FinanceiroService.get_fatura_referencia(id_contrato=id_contrato)

        # Dados fatura
        fatura_parcial = {"valor_fatura": None, "dia_vencimento_fatura": None}

        if fatura_referencia:
            fatura_parcial["valor_fatura"] = fatura_referencia["valor"]
            fatura_parcial["dia_vencimento_fatura"] = fatura_referencia[
                "dia_vencimento_fatura"
            ]

        return schemas.ContratoOutSchema(
            id=contrato["id"],
            id_login=login.get("id"),
            id_cliente=id_cliente,
            nome_cliente=nome_cliente,
            status=contrato["status"],
            status_acesso=contrato["status_internet"],
            nome_plano=contrato["contrato"],
            valor_fatura=fatura_parcial["valor_fatura"],
            dia_vencimento_fatura=fatura_parcial["dia_vencimento_fatura"],
            mac_onu=login.get("onu_mac"),
        )

    @staticmethod
    async def get_contratos(
        protocolo: str | None,
        cnpj_cpf: str | None,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.ListOutSchema[schemas.ContratoOutSchema]:
        # --- Obtém contratos ativos ---
        contratos = await ClientService.get_contratos_ativos(
            protocolo=protocolo,
            cnpj_cpf=cnpj_cpf,
            pagina=pagina,
            itens_por_pagina=itens_por_pagina,
        )

        return schemas.ListOutSchema[schemas.ContratoOutSchema](
            data=[schemas.ContratoOutSchema(**c) for c in contratos],
            meta=schemas.MetaOutSchema(
                total_itens=len(contratos),
                pagina_atual=pagina or 1,
                itens_por_pagina=itens_por_pagina or 10,
            ),
        )

    @classmethod
    async def get_status_conexao(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ) -> schemas.StatusConexaoOutSchema:
        # --- Obtém login ---
        login = await cls._get_login(id_login=id_login)

        return schemas.StatusConexaoOutSchema(status_conexao=login["online"])

    @classmethod
    async def get_status_onu(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt | None = None,
        mac_onu: str | None = None,
    ) -> schemas.StatusOnuOutSchema:
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
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
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

        return schemas.StatusOnuOutSchema(status_onu=sinal_rx)

    @staticmethod
    async def post_desconectar_cliente(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ) -> schemas.MensagemOutSchema:
        # --- Realiza desconexão de cliente ---
        payload = {"id": id_login}
        endpoint = "desconectar_clientes"
        res = await clients.IxcClient.post(endpoint=endpoint, payload=payload)
        type = res["msg"][0]["type"]
        if type == "error":
            msgs = res.get("msg", [])
            msg = msgs[0].get("message", "Desconexão malsucedida")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=utils.Formatter.sanitize(string=msg),
            )

        return schemas.MensagemOutSchema(mensagem="Desconexão bem-sucedida")

    @staticmethod
    async def get_atendimentos(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.ListOutSchema[schemas.AtendimentoOutSchema]:
        # --- Obtém atendimentos abertos ---
        endpoint = "su_ticket"
        grid_param = [
            utils.Param(TB="su_ticket.id_login", P=id_login),
            utils.Param(TB="su_ticket.su_status", OP="!=", P="S"),
            utils.Param(TB="su_ticket.su_status", OP="!=", P="C"),
        ]
        res = await clients.IxcClient.get(
            endpoint=endpoint,
            grid_param=grid_param,
            pagina=pagina,
            itens_por_pagina=itens_por_pagina,
        )
        atendimentos = res.get("registros", [])
        total = res.get("total", 0)

        atendimentos_parciais: list[schemas.AtendimentoOutSchema] = []

        # Iteração entre atendimentos
        for atendimento in atendimentos:
            # Data criação
            datetime_criacao = atendimento["data_criacao"]
            data_criacao = datetime_criacao.split(" ")[0]

            # Atendimentos parciais
            atendimentos_parciais.append(
                schemas.AtendimentoOutSchema(
                    id=atendimento["id"],
                    id_assunto=atendimento["id_assunto"],
                    status=atendimento["su_status"],
                    mensagem=atendimento["menssagem"],
                    titulo=atendimento["titulo"],
                    data_criacao=data_criacao,
                )
            )

        return schemas.ListOutSchema[schemas.AtendimentoOutSchema](
            data=atendimentos_parciais,
            meta=schemas.MetaOutSchema(
                itens_por_pagina=itens_por_pagina or 10,
                pagina_atual=pagina or 1,
                total_itens=total,
            ),
        )

    @staticmethod
    async def post_atendimentos(
        atendimento: schemas.AtendimentoInSchema,
    ) -> schemas.AtendimentoOutSchema:
        # --- Cria atendimento ---
        endpoint = "su_ticket"
        payload = atendimento.model_dump()
        menssagem = payload["mensagem"]
        del payload["mensagem"]
        payload["menssagem"] = menssagem
        res = await clients.IxcClient.post(endpoint=endpoint, payload=payload)
        if not (id := res.get("id")):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cadastro malsucedido",
            )

        # --- Obtém atendimento criado ---
        grid_param = [utils.Param(TB="su_ticket.id", P=id)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        regs = res.get("registros", [])
        atendimento_criado = regs[0]

        # Data criação
        datetime_criacao = atendimento_criado["data_criacao"]
        data_criacao = datetime_criacao.split(" ")[0]

        return schemas.AtendimentoOutSchema(
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
    ) -> schemas.IpOutSchema:
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
        res = await clients.IxcClient.put(endpoint=endpoint, id=id, payload=payload)
        if res["type"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Atualização malsucedida",
            )

        return schemas.IpOutSchema(ip=novo_ip, pool_radius=int(novo_radius))

    @staticmethod
    async def post_limpar_mac(
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ) -> schemas.MensagemOutSchema:
        # --- Realiza limpeza de MAC ---
        endpoint = "radusuarios_25452"
        payload = {"get_id": id_login}
        res = await clients.IxcClient.post(endpoint=endpoint, payload=payload)
        if res["type"] == "error":
            msg = res.get("message", "Limpeza malsucedida")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=utils.Formatter.sanitize(string=msg),
            )

        return schemas.MensagemOutSchema(mensagem="Limpeza bem-sucedida")

    @classmethod
    async def get_dados_wifi(
        cls,
        # IDs NonNegativeInt, pois o IXC é quebrado
        id_login: NonNegativeInt,
    ) -> schemas.WifiOutSchema:
        # --- Obtém login ---
        login = await cls._get_login(id_login=id_login)

        return schemas.WifiOutSchema(
            ssid_wifi_2g=login["ssid_router_wifi"] or None,
            senha_wifi_2g=login["senha_rede_sem_fio"] or None,
            ssid_wifi_5g=login["ssid_router_wifi_5ghz"] or None,
            senha_wifi_5g=login["senha_rede_sem_fio_5ghz"] or None,
        )
