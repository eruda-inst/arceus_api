"""
Service for support operations (connection, ONU, tickets, WiFi, etc.).
"""

import datetime as dt
import re
from typing import Any

from fastapi import HTTPException, status
from httpx2 import QueryParams
from pydantic import NonNegativeInt, PositiveInt

from .. import clients, schemas, services, utils


class SupportService:
    """
    Provides static/class methods for support operations.
    """

    @staticmethod
    async def _get_login(
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
    ) -> dict[str, Any]:
        """
        Retrieve a login (radusuarios) by ID from IXC.

        Args:
            login_id: Login ID in IXC.

        Returns:
            The login record as a dictionary.

        Raises:
            HTTPException: 404 if the login does not exist.
        """
        # --- Get login ---
        endpoint = "radusuarios"
        grid_param = [utils.Param(TB="radusuarios.id", P=login_id)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Login inexistente"
            )
        login = regs[0]

        return login

    @classmethod
    async def _get_device(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
    ) -> dict[str, Any]:
        """
        Retrieve a device associated with a login from the IXC ACS system.

        Args:
            login_id: Login ID in IXC.

        Returns:
            The device record as a dictionary.

        Raises:
            HTTPException: 404 if the device does not exist.
        """
        # --- Get login ---
        login = await cls._get_login(login_id=login_id)

        # --- Get device ---
        endpoint = "devices/views/natural"
        query_params = QueryParams(
            {
                "search[column]": "connection.pppoeLogin",
                "search[search]": login["login"],
            }
        )
        res = await clients.IxcAcsClient.get(
            endpoint=endpoint, query_params=query_params
        )
        if not (regs := res.get("registers", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo inexistente"
            )
        device = regs[0]

        return device

    @classmethod
    async def get_dns_server(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
    ) -> schemas.DnsServerOut:
        """
        Retrieve the DNS server configured on a login's device.

        Args:
            login_id: Login ID in IXC.

        Returns:
            DnsServerOut with the DNS server.

        Raises:
            HTTPException: 404 if the WAN interface is not found.
        """
        # --- Get device ---
        device = await cls._get_device(login_id=login_id)

        # --- Get WAN ---
        endpoint = f"devices/{device['serialNumber']}/ethernet/ppp"
        ethernet = await clients.IxcAcsClient.get(endpoint=endpoint)
        if ethernet is None or not len(ethernet):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="WAN inexistente"
            )

        return schemas.DnsServerOut(dns_server=ethernet[0]["dnsServer"])

    @classmethod
    async def get_has_ipv6(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
    ) -> schemas.HasIPV6OutSchema:
        """
        Check whether a login's device has IPv6 enabled.

        Args:
            login_id: Login ID in IXC.

        Returns:
            HasIPV6OutSchema indicating IPv6 presence.

        Raises:
            HTTPException: 404 if the device info is not found.
        """
        # --- Get device ---
        device = await cls._get_device(login_id=login_id)
        serial_number = device["serialNumber"]

        # --- Get IPV6 ---
        endpoint = "devices/views/ipv6"
        query_params = QueryParams(
            {"search[column]": "serialNumber", "search[search]": serial_number}
        )
        res = await clients.IxcAcsClient.get(
            endpoint=endpoint, query_params=query_params
        )

        if not (regs := res.get("registers", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispositivos inexistentes",
            )
        info = regs[0]

        tem_ipv6 = info["deviceInfo"]["ipv6"] != ""

        return schemas.HasIPV6OutSchema(tem_ipv6=tem_ipv6)

    @classmethod
    async def get_uptime(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
    ) -> schemas.UptimeOutSchema:
        """
        Retrieve the uptime of a login's device.

        Args:
            login_id: Login ID in IXC.

        Returns:
            UptimeOutSchema formatted as DD:HH:MM:SS.
        """
        # --- Get device ---
        device = await cls._get_device(login_id=login_id)

        uptime_seconds = device["deviceInfo"]["uptime"]
        uptime = dt.timedelta(seconds=uptime_seconds)

        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds // 60) % 60
        seconds = uptime.seconds % 60

        uptime_out = f"{days:02}D {hours:02}H {minutes:02}M {seconds:02}S"

        return schemas.UptimeOutSchema(uptime=uptime_out)

    @classmethod
    async def get_fiber_signal(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
    ) -> schemas.FiberSignalOutSchema:
        """
        Retrieve the fiber signal (RX/TX) for a login's device.

        Args:
            login_id: Login ID in IXC.

        Returns:
            FiberSignalOutSchema with rx and tx values.
        """
        # --- Get device ---
        device = await cls._get_device(login_id=login_id)

        rx = device["deviceInfo"]["rx"]
        tx = device["deviceInfo"]["tx"]

        return schemas.FiberSignalOutSchema(rx=rx, tx=tx)

    @staticmethod
    async def get_contracts(
        protocol: str | None,
        cnpj_cpf: str | None,
        page: PositiveInt,
        items_per_page: PositiveInt,
    ) -> schemas.ListOutSchema[schemas.ContractOutSchema]:
        """
        Retrieve active contracts for a customer.

        Args:
            protocol: OPA protocol.
            cnpj_cpf: Customer document.
            page: Page number.
            items_per_page: Items per page.

        Returns:
            A ListOutSchema of ContractOutSchema.
        """
        # --- Get active contracts ---
        contracts = await services.CustomerService.get_active_contracts(
            protocol=protocol,
            cnpj_cpf=cnpj_cpf,
            page=page,
            items_per_page=items_per_page,
        )

        return schemas.ListOutSchema[schemas.ContractOutSchema](
            data=[schemas.ContractOutSchema(**c) for c in contracts],
            meta=schemas.MetaOutSchema(
                total_itens=len(contracts),
                pagina_atual=page,
                itens_por_pagina=items_per_page,
            ),
        )

    @classmethod
    async def get_connection_status(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
    ) -> schemas.ConnectionStatusOutSchema:
        """
        Retrieve the connection status for a login.

        Args:
            login_id: Login ID in IXC.

        Returns:
            ConnectionStatusOutSchema with the connection status.
        """
        # --- Get login ---
        login = await cls._get_login(login_id=login_id)
        return schemas.ConnectionStatusOutSchema(status_conexao=login["online"])

    @classmethod
    async def get_onu_status(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt | None = None,
        onu_mac: str | None = None,
    ) -> schemas.OnuStatusOutSchema:
        """
        Retrieve the ONU RX signal status.

        Uses the MAC address if provided (cheaper), otherwise falls back to
        fetching the login by ID to obtain the ONU MAC.

        Args:
            login_id: Login ID in IXC.
            onu_mac: ONU MAC address.

        Returns:
            OnuStatusOutSchema with the ONU signal level.

        Raises:
            HTTPException: 400 if neither parameter is provided.
            HTTPException: 404 if the ONU or signal is not found.
        """
        # Justification for this approach: IXC
        query_value = None

        # MAC is priority, because computational costs is lower (less one request)
        if onu_mac is not None and not re.match(pattern=r"{{\w+}}", string=onu_mac):
            query_value = onu_mac
        elif login_id is not None:
            # --- Get login ---
            login = await cls._get_login(login_id=login_id)

            query_value = login["onu_mac"]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça id_login ou mac_onu",
            )

        # --- Get ONU by MAC ---
        endpoint = "radpop_radio_cliente_fibra"
        grid_param = [utils.Param(TB="radpop_radio_cliente_fibra.mac", P=query_value)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        if not (regs := res.get("registros", [])):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="ONU inexistente"
            )
        onu = regs[0]

        if not (rx_signal := onu.get("sinal_rx")):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sinal ONU inexistente",
            )

        return schemas.OnuStatusOutSchema(status_onu=rx_signal)

    @staticmethod
    async def post_disconnect_customer(
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
    ) -> schemas.MessageOutSchema:
        """
        Send a disconnection signal to a customer's login.

        Args:
            login_id: Login ID in IXC.

        Returns:
            MessageOutSchema indicating success.

        Raises:
            HTTPException: 500 if the disconnection fails.
        """
        # --- Post disconnection ---
        payload = {"id": login_id}
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

        return schemas.MessageOutSchema(mensagem="Desconexão bem-sucedida")

    @staticmethod
    async def get_tickets(
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
        page: PositiveInt,
        items_per_page: PositiveInt,
    ) -> schemas.ListOutSchema[schemas.TicketOutSchema]:
        """
        Retrieve open tickets for a login.

        Args:
            login_id: Login ID in IXC.
            page: Page number.
            items_per_page: Items per page.

        Returns:
            A ListOutSchema of TicketOutSchema.
        """
        # --- Get tickets ---
        endpoint = "su_ticket"
        grid_param = [
            utils.Param(TB="su_ticket.id_login", P=login_id),
            utils.Param(TB="su_ticket.su_status", OP="!=", P="S"),
            utils.Param(TB="su_ticket.su_status", OP="!=", P="C"),
        ]
        res = await clients.IxcClient.get(
            endpoint=endpoint,
            grid_param=grid_param,
            pagina=page,
            itens_por_pagina=items_per_page,
        )
        tickets = res.get("registros", [])
        total = res.get("total", 0)

        partial_tickets: list[schemas.TicketOutSchema] = []

        for ticket in tickets:
            creation_datetime = ticket["data_criacao"]
            creation_date = creation_datetime.split(" ")[0]

            partial_tickets.append(
                schemas.TicketOutSchema(
                    id=ticket["id"],
                    id_assunto=ticket["id_assunto"],
                    status=ticket["su_status"],
                    mensagem=ticket["menssagem"],
                    titulo=ticket["titulo"],
                    data_criacao=creation_date,
                )
            )

        return schemas.ListOutSchema[schemas.TicketOutSchema](
            data=partial_tickets,
            meta=schemas.MetaOutSchema(
                itens_por_pagina=items_per_page,
                pagina_atual=page,
                total_itens=total,
            ),
        )

    @staticmethod
    async def post_tickets(
        ticket: schemas.TicketInSchema,
    ) -> schemas.TicketOutSchema:
        """
        Create a new support ticket.

        Args:
            ticket: Ticket input data.

        Returns:
            TicketOutSchema with the created ticket.

        Raises:
            HTTPException: 500 if creation fails.
        """
        # --- Post ticket ---
        endpoint = "su_ticket"
        payload = ticket.model_dump()
        menssagem = payload["mensagem"]
        del payload["mensagem"]
        payload["menssagem"] = menssagem
        res = await clients.IxcClient.post(endpoint=endpoint, payload=payload)
        if not (id := res.get("id")):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cadastro malsucedido",
            )

        # --- Get ticket ---
        grid_param = [utils.Param(TB="su_ticket.id", P=id)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        regs = res.get("registros", [])
        created_ticket = regs[0]

        creation_datetime = created_ticket["data_criacao"]
        creation_date = creation_datetime.split(" ")[0]

        return schemas.TicketOutSchema(
            id=created_ticket["id"],
            data_criacao=creation_date,
            id_assunto=created_ticket["id_assunto"],
            status=created_ticket["su_status"],
            mensagem=created_ticket["menssagem"],
            titulo=created_ticket["titulo"],
        )

    @classmethod
    async def patch_ip(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
        ip: str | None = None,
        pool_radius: str | None = None,
    ) -> schemas.IpOutSchema:
        """
        Update IP and/or radius pool for a login.

        Args:
            login_id: Login ID in IXC.
            ip: New IP (optional).
            pool_radius: New radius pool (optional).

        Returns:
            IpOutSchema with the updated values.

        Raises:
            HTTPException: 400 if neither parameter is provided.
            HTTPException: 500 if the update fails.
        """
        if ip is None and pool_radius is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça ip ou pool_radius",
            )

        # --- Get login ---
        old_login = await cls._get_login(login_id=login_id)

        new_ip = ip if ip else old_login["ip"]
        new_radius = pool_radius if pool_radius else old_login["pool_radius"]
        updated_login: Any = {
            **old_login,
            "ip": new_ip or "",
            "pool_radius": new_radius or "",
        }
        del updated_login["id"]

        # --- Put login ---
        endpoint = "radusuarios"
        res = await clients.IxcClient.put(
            endpoint=f"{endpoint}/{login_id}", payload=updated_login
        )
        if res["type"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Atualização malsucedida",
            )

        return schemas.IpOutSchema(ip=new_ip, pool_radius=int(new_radius))

    @staticmethod
    async def post_clear_mac(
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
    ) -> schemas.MessageOutSchema:
        """
        Clear the MAC address of a login.

        Args:
            login_id: Login ID in IXC.

        Returns:
            MessageOutSchema indicating success.

        Raises:
            HTTPException: 500 if the operation fails.
        """
        # --- Post MAC clearing ---
        endpoint = "radusuarios_25452"
        payload = {"get_id": login_id}
        res = await clients.IxcClient.post(endpoint=endpoint, payload=payload)
        if res["type"] == "error":
            msg = res.get("message", "Limpeza malsucedida")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=utils.Formatter.sanitize(string=msg),
            )

        return schemas.MessageOutSchema(mensagem="Limpeza bem-sucedida")

    @classmethod
    async def get_wifi_data(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
    ) -> schemas.WifiOutSchema:
        """
        Retrieve WiFi configuration (2G and 5G) for a login.

        Args:
            login_id: Login ID in IXC.

        Returns:
            WifiOutSchema with SSIDs and passwords.
        """
        # --- Get login ---
        login = await cls._get_login(login_id=login_id)

        return schemas.WifiOutSchema(
            ssid_wifi_2g=login["ssid_router_wifi"] or None,
            senha_wifi_2g=login["senha_rede_sem_fio"] or None,
            ssid_wifi_5g=login["ssid_router_wifi_5ghz"] or None,
            senha_wifi_5g=login["senha_rede_sem_fio_5ghz"] or None,
        )

    @classmethod
    async def patch_wifi_data(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
        ssid: str | None = None,
        ssid_pass: str | None = None,
    ) -> schemas.MessageOutSchema:
        """
        Update WiFi SSID and/or password on both 2G and 5G interfaces.

        Args:
            login_id: Login ID in IXC.
            ssid: New SSID (optional).
            ssid_pass: New password (optional).

        Returns:
            MessageOutSchema indicating success.

        Raises:
            HTTPException: 404 if the WiFi data or enabled interfaces are missing.
        """
        # --- Get device ---
        device = await cls._get_device(login_id=login_id)
        serial_number = device["serialNumber"]

        # --- Get wifi ---
        endpoint = f"devices/{device['serialNumber']}/wifi"
        wifi = await clients.IxcAcsClient.get(endpoint=endpoint)
        if wifi is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Wifi inexistente"
            )

        interface_2g = next(i for i in wifi["2.4"] if i["enable"])
        interface_5g = next(i for i in wifi["5.8"] if i["enable"])

        payload_2g = {}
        payload_5g = {}

        if ssid is not None:
            payload_2g["ssid"] = ssid
            # Append the 5G suffix to differentiate the 5G network
            payload_5g["ssid"] = f"{ssid}_5G"

        if ssid_pass is not None:
            payload_2g["password"] = ssid_pass
            payload_5g["password"] = ssid_pass

        # --- Patch wifi 2 G ---
        await clients.IxcAcsClient.patch(
            endpoint=f"devices/{serial_number}/wifi/{interface_2g['id']}",
            payload=payload_2g,
        )

        # --- Patch wifi 5 G ---
        await clients.IxcAcsClient.patch(
            endpoint=f"devices/{serial_number}/wifi/{interface_5g['id']}",
            payload=payload_5g,
        )

        return schemas.MessageOutSchema(mensagem="Atualização bem-sucedida")
