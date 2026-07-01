from typing import Any
from . import service_service
from .. import clients, schemas
from pydantic import PositiveInt
from fastapi import HTTPException, status


class VilaService(service_service.Service):
    @classmethod
    async def get_login(cls, numero_residencia: PositiveInt) -> dict[str, Any]:
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
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Nenhum login encontrado.",
                )
            login = regs[0]

            return {
                "id": int(login["id"]),
                "login": login["login"],
                "online": login["online"],
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
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    @classmethod
    async def get_status_conexao(
        cls, numero_residencia: PositiveInt
    ) -> schemas.NewStatusConexaoOut:
        try:
            # --- Login ---
            login = await cls.get_login(numero_residencia=numero_residencia)

            # Exceção já tratada na get_login

            return schemas.NewStatusConexaoOut(status_conexao=login["online"])
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    @classmethod
    async def get_status_onu(
        cls, numero_residencia: PositiveInt
    ) -> schemas.StatusOnuOut:
        try:
            # --- Login ---
            login = await cls.get_login(numero_residencia=numero_residencia)

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
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Nenhuma ONU encontrada.",
                )
            onu = regs[0]

            return schemas.StatusOnuOut(status_onu=onu["sinal_rx"])
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    @classmethod
    async def get_dados_wifi(cls, numero_residencia: PositiveInt) -> schemas.NewWifiOut:
        try:
            # --- Login ---
            login = await cls.get_login(numero_residencia=numero_residencia)

            # Exceção já tratada na get_login

            return schemas.NewWifiOut(
                ssid_wifi_2g=login["ssid_router_wifi"],
                senha_wifi_2g=login["senha_rede_sem_fio"],
                ssid_wifi_5g=login["ssid_router_wifi_5ghz"],
                senha_wifi_5g=login["senha_rede_sem_fio_5ghz"],
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    @classmethod
    async def get_atendimentos(
        cls,
        numero_residencia: PositiveInt,
        page: PositiveInt | None,
        per_page: PositiveInt | None,
    ) -> schemas.AtendimentoOut:
        try:
            # --- Login ---
            login = await cls.get_login(numero_residencia=numero_residencia)

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
                endpoint=endpoint, grid_param=grid_param, page=page, per_page=per_page
            )
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sem atendimentos abertos.",
                )
            total = res["total"]
            atendimentos = regs

            atendimentos_parciais: list[schemas.Atendimento] = []

            # --- Iteração entre atendimentos ---
            for atendimento in atendimentos:
                atendimentos_parciais.append(
                    schemas.Atendimento(
                        id=atendimento["id"],
                        id_assunto=atendimento["id_assunto"],
                        status=atendimento["su_status"],
                        mensagem=atendimento["menssagem"],
                        titulo=atendimento["titulo"],
                        data_criacao=atendimento["data_criacao"],
                    ),
                )

            return schemas.AtendimentoOut(
                data=atendimentos_parciais,
                meta=schemas.Meta(total=total, page=page, per_page=per_page),
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    @classmethod
    async def post_limpar_mac(
        cls, numero_residencia: PositiveInt
    ) -> schemas.MensagemOut:
        try:
            # --- Login ---
            login = await cls.get_login(numero_residencia=numero_residencia)

            # Exceção já tratada na get_login

            # --- Limpar MAC ---
            endpoint = "radusuarios_25452"
            payload = {"get_id": str(login["id"])}
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)

            return schemas.MensagemOut(
                mensagem=res.get("message", "Nenhuma mensagem retornada.")
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )
