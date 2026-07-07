from typing import Any
from .. import clients, schemas
from pydantic import PositiveInt
from fastapi import HTTPException, status


class VilaService:
    @staticmethod
    async def _get_login(numero_residencia: PositiveInt) -> dict[str, Any]:
        try:
            # --- Login ---
            endpoint = "radusuarios"
            grid_param = [
                {
                    "TB": "radusuarios.login",
                    "OP": "L",
                    "P": f"res{str(numero_residencia)}",
                },
                {"TB": "radusuarios.ativo", "OP": "=", "P": "S"},
            ]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Login inexistente."
                )
            login = regs[0]

            return {
                "id": int(login["id"]),
                "login": login["login"],
                "online": login["online"],
                "id_cliente": int(login["id_cliente"]),
                "ssid_router_wifi": login["ssid_router_wifi"],
                "senha_rede_sem_fio": login["senha_rede_sem_fio"],
                "ssid_router_wifi_5ghz": login["ssid_router_wifi_5ghz"],
                "senha_rede_sem_fio_5ghz": login["senha_rede_sem_fio_5ghz"],
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @classmethod
    async def get_contrato(
        cls, numero_residencia: PositiveInt
    ) -> schemas.VilaContratoOut:
        try:
            # --- Login ---
            login = await cls._get_login(numero_residencia=numero_residencia)

            # Exceção já tratada na get_login

            # --- Contrato ---
            endpoint = "cliente_contrato"
            grid_param = [
                {
                    "TB": "cliente_contrato.id_cliente",
                    "OP": "=",
                    "P": str(login["id_cliente"]),
                }
            ]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Contrato inexistente.",
                )
            contrato = regs[0]

            return schemas.VilaContratoOut(
                id=contrato["id"],
                id_login=login["id"],
                id_cliente=contrato["id_cliente"],
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @classmethod
    async def get_status_conexao(
        cls, numero_residencia: PositiveInt
    ) -> schemas.StatusConexaoOut:
        try:
            # --- Login ---
            login = await cls._get_login(numero_residencia=numero_residencia)

            # Exceção já tratada na get_login

            return schemas.StatusConexaoOut(status_conexao=login["online"])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @classmethod
    async def get_status_onu(
        cls, numero_residencia: PositiveInt
    ) -> schemas.StatusOnuOut:
        try:
            # --- Login ---
            login = await cls._get_login(numero_residencia=numero_residencia)

            # Exceção já tratada na get_login

            # --- ONU ---
            endpoint = "radpop_radio_cliente_fibra"
            grid_param = [
                {
                    "TB": "radpop_radio_cliente_fibra.id_login",
                    "OP": "=",
                    "P": f"res{str(login['id'])}",
                },
            ]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="ONU inexistente."
                )
            onu = regs[0]

            return schemas.StatusOnuOut(status_onu=onu["sinal_rx"])
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @classmethod
    async def get_dados_wifi(cls, numero_residencia: PositiveInt) -> schemas.WifiOut:
        try:
            # --- Login ---
            login = await cls._get_login(numero_residencia=numero_residencia)

            # Exceção já tratada na get_login

            return schemas.WifiOut(
                ssid_wifi_2g=login["ssid_router_wifi"],
                senha_wifi_2g=login["senha_rede_sem_fio"],
                ssid_wifi_5g=login["ssid_router_wifi_5ghz"],
                senha_wifi_5g=login["senha_rede_sem_fio_5ghz"],
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno desconhecido: {e}",
            )

    @classmethod
    async def get_atendimentos(
        cls,
        numero_residencia: PositiveInt,
        pagina: PositiveInt | None,
        itens_por_pagina: PositiveInt | None,
    ) -> schemas.AtendimentoListOut:
        try:
            # --- Login ---
            login = await cls._get_login(numero_residencia=numero_residencia)

            # Exceção já tratada na get_login

            # --- Atendimentos ---
            endpoint = "su_ticket"
            grid_param = [
                {
                    "TB": "su_ticket.id_login",
                    "OP": "L",
                    "P": f"res{str(login['id'])}",
                },
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
            total = res["total"]
            atendimentos = regs

            atendimentos_parciais: list[schemas.AtendimentoOut] = []

            # --- Iteração entre atendimentos ---
            for atendimento in atendimentos:
                atendimentos_parciais.append(
                    schemas.AtendimentoOut(
                        id=atendimento["id"],
                        id_assunto=atendimento["id_assunto"],
                        status=atendimento["su_status"],
                        mensagem=atendimento["menssagem"],
                        titulo=atendimento["titulo"],
                        data_criacao=atendimento["data_criacao"],
                    ),
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

    @classmethod
    async def post_limpar_mac(
        cls, numero_residencia: PositiveInt
    ) -> schemas.MensagemOut:
        try:
            # --- Login ---
            login = await cls._get_login(numero_residencia=numero_residencia)

            # Exceção já tratada na get_login

            # --- Limpar MAC ---
            endpoint = "radusuarios_25452"
            payload = {"get_id": str(login["id"])}
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

    @classmethod
    async def post_desconectar_cliente(
        cls, numero_residencia: PositiveInt
    ) -> schemas.MensagemOut:
        try:
            # --- Login ---
            login = await cls._get_login(numero_residencia=numero_residencia)

            # Exceção já tratada na get_login

            # --- Desconectar cliente ---
            endpoint = "desconectar_clientes"
            payload = {"id": str(login["id"])}
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)
            type = res["msg"][0]["type"]
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
    async def post_atendimentos(
        atendimento: schemas.AtendimentoIn,
    ) -> schemas.AtendimentoOut:
        try:
            # --- Atendimento ---
            endpoint = "su_ticket"
            payload = atendimento.model_dump()
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)
            id = res.get("id")
            if not id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Cadastro malsucedido.",
                )

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
