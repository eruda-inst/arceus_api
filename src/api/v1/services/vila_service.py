import re
from typing import Any

from fastapi import HTTPException, status
from pydantic import PositiveInt
from starlette.status import HTTP_400_BAD_REQUEST

from .. import clients, schemas, utils


class VilaService:
    @staticmethod
    async def _get_login(
        numero_residencia: PositiveInt | None = None, pppoe: str | None = None
    ) -> dict[str, Any]:
        search_pppoe = None

        if numero_residencia is not None:
            search_pppoe = f"res{numero_residencia}"
        elif pppoe is not None and not re.match(pattern=r"{{\w+}}", string=pppoe):
            search_pppoe = pppoe
        else:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Forneça numero_ressidencia ou ppppoe",
            )

        # --- Obtém login ---
        endpoint = "radusuarios"
        grid_param = [
            utils.Param(TB="radusuarios.login", OP="L", P=search_pppoe),
            utils.Param(TB="radusuarios.ativo", P="S"),
        ]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Login inexistente"
            )
        login = regs[0]

        return {
            "id": int(login["id"]),
            "login": login["login"],
            "online": login["online"],
            "id_cliente": int(login["id_cliente"]),
            "ssid_router_wifi": login.get("ssid_router_wifi"),
            "senha_rede_sem_fio": login.get("senha_rede_sem_fio"),
            "ssid_router_wifi_5ghz": login.get("ssid_router_wifi_5ghz"),
            "senha_rede_sem_fio_5ghz": login.get("senha_rede_sem_fio_5ghz"),
        }

    @classmethod
    async def get_contrato(
        cls, numero_residencia: PositiveInt | None = None, pppoe: str | None = None
    ) -> schemas.VilaContratoOutSchema:
        # --- Obtém login ---
        login = await cls._get_login(numero_residencia=numero_residencia, pppoe=pppoe)

        # --- Obtém contrato ---
        endpoint = "cliente_contrato"
        grid_param = [
            utils.Param(TB="cliente_contrato.id_cliente", P=login["id_cliente"])
        ]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contrato inexistente",
            )
        contrato = regs[0]

        return schemas.VilaContratoOutSchema(
            id=contrato["id"],
            id_login=login["id"],
            id_cliente=contrato["id_cliente"],
        )

    @classmethod
    async def get_status_conexao(
        cls, numero_residencia: PositiveInt | None, pppoe: str | None
    ) -> schemas.StatusConexaoOutSchema:
        # --- Obtém login ---
        login = await cls._get_login(numero_residencia=numero_residencia, pppoe=pppoe)

        return schemas.StatusConexaoOutSchema(status_conexao=login["online"])

    @classmethod
    async def get_status_onu(
        cls, numero_residencia: PositiveInt | None, pppoe: str | None
    ) -> schemas.StatusOnuOutSchema:
        # --- Obtém login ---
        login = await cls._get_login(numero_residencia=numero_residencia, pppoe=pppoe)

        # --- Obtém ONU ---
        endpoint = "radpop_radio_cliente_fibra"
        grid_param = [
            utils.Param(TB="radpop_radio_cliente_fibra.id_login", P=f"res{login['id']}")
        ]
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

    @classmethod
    async def get_atendimentos(
        cls,
        numero_residencia: PositiveInt | None,
        pppoe: str | None,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.ListOutSchema[schemas.AtendimentoOutSchema]:
        # --- Obtém login ---
        login = await cls._get_login(numero_residencia=numero_residencia, pppoe=pppoe)

        # --- Obtém atendimentos abertos ---
        endpoint = "su_ticket"
        grid_param = [
            utils.Param(TB="su_ticket.id_login", OP="L", P=f"res{login['id']}"),
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
            atendimentos_parciais.append(
                schemas.AtendimentoOutSchema(
                    id=atendimento["id"],
                    id_assunto=atendimento["id_assunto"],
                    status=atendimento["su_status"],
                    mensagem=atendimento["menssagem"],
                    titulo=atendimento["titulo"],
                    data_criacao=atendimento["data_criacao"],
                ),
            )

        return schemas.ListOutSchema[schemas.AtendimentoOutSchema](
            data=atendimentos_parciais,
            meta=schemas.MetaOutSchema(
                total_itens=total,
                pagina_atual=pagina or 1,
                itens_por_pagina=itens_por_pagina or 10,
            ),
        )

    @classmethod
    async def post_limpar_mac(
        cls, numero_residencia: PositiveInt | None, pppoe: str | None
    ) -> schemas.MensagemOutSchema:
        # --- Obtém login ---
        login = await cls._get_login(numero_residencia=numero_residencia, pppoe=pppoe)

        # --- Realiza limpeza de MAC ---
        endpoint = "radusuarios_25452"
        payload = {"get_id": str(login["id"])}
        res = await clients.IxcClient.post(endpoint=endpoint, payload=payload)
        if res["type"] == "error":
            msg = res.get("message", "Limpeza malsucedida")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=utils.Formatter.sanitize(string=msg),
            )

        return schemas.MensagemOutSchema(mensagem="Limpeza bem-sucedida")

    @classmethod
    async def post_desconectar_cliente(
        cls, numero_residencia: PositiveInt | None, pppoe: str | None
    ) -> schemas.MensagemOutSchema:
        # --- Obtém login ---
        login = await cls._get_login(numero_residencia=numero_residencia, pppoe=pppoe)

        # --- Realiza desconexão de cliente ---
        endpoint = "desconectar_clientes"
        payload = {"id": str(login["id"])}
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
    async def post_atendimentos(
        atendimento: schemas.AtendimentoInSchema,
    ) -> schemas.AtendimentoOutSchema:
        # --- Cria atendimento ---
        endpoint = "su_ticket"
        payload = atendimento.model_dump()
        payload["menssagem"] = atendimento.mensagem
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
        if not regs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Atendimento inexistente",
            )
        atendimento_criado = regs[0]

        return schemas.AtendimentoOutSchema(
            id=atendimento_criado["id"],
            data_criacao=atendimento_criado["data_criacao"],
            id_assunto=atendimento_criado["id_assunto"],
            status=atendimento_criado["su_status"],
            mensagem=atendimento_criado["menssagem"],
            titulo=atendimento_criado["titulo"],
        )
