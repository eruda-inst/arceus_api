import re
from typing import Any

from fastapi import HTTPException, status
from pydantic import NonNegativeInt, PositiveInt
from starlette.status import HTTP_400_BAD_REQUEST

from .. import clients, schemas, utils


class VillageService:
    @staticmethod
    async def _get_login(
        # IDs NonNegativeInt, pois o IXC é quebrado
        login_id: NonNegativeInt | None = None,
        residence_number: PositiveInt | None = None,
        pppoe: str | None = None,
    ) -> dict[str, Any]:
        search_key = None
        search_value = None

        if login_id is not None:
            search_key = "id"
            search_value = login_id
        elif residence_number is not None:
            search_key = "login"
            search_value = f"res{residence_number}"
        elif pppoe is not None and not re.match(pattern=r"{{\w+}}", string=pppoe):
            search_key = "login"
            search_value = pppoe
        else:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Forneça numero_residencia ou ppppoe",
            )

        # --- Obtém login ---
        endpoint = "radusuarios"
        grid_param = [
            utils.Param(
                TB=f"radusuarios.{search_key}",
                OP="L" if search_key == "login" else "=",
                P=search_value,
            ),
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
    async def get_contract(
        cls, residence_number: PositiveInt | None = None, pppoe: str | None = None
    ) -> schemas.VillageContractOutSchema:
        # --- Obtém login ---
        login = await cls._get_login(residence_number=residence_number, pppoe=pppoe)

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
        contract = regs[0]

        return schemas.VillageContractOutSchema(
            id=contract["id"],
            id_login=login["id"],
            id_cliente=contract["id_cliente"],
        )
