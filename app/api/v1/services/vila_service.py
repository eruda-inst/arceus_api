from . import service_service
from .. import clients, schemas
from pydantic import PositiveInt
from fastapi import HTTPException, status


class VilaService(service_service.Service):
    @classmethod
    async def get_login(cls, numero_residencia: PositiveInt):
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
                "id": login["id"],
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
        except HTTPException:
            raise
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
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )
