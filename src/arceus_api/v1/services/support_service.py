import datetime as dt
from typing import Any

from fastapi import HTTPException, status
from httpx2 import QueryParams
from pydantic import NonNegativeInt, PositiveInt

from .. import clients, schemas, services, utils


class SupportService:
    @staticmethod
    async def _get_login(
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt | None = None,
        onu_mac: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Retrieve an IXC login record by IXC login ID or ONU MAC address.

        Args:
            login_id (NonNegativeInt | None): IXC login ID to search for. Optional (default: None).
            onu_mac (str | None): ONU MAC address to search for. Optional (default: None).

        Returns:
            dict[str, Any] | None: First matching IXC login record, or None if no identifier is provided or no record is found.
        """
        if login_id is not None:
            query_field = "id"
            query_value = login_id
        elif onu_mac is not None:
            query_field = "onu_mac"
            query_value = onu_mac
        else:
            return None

        # --- Get login (IXC) ---
        endpoint = "radusuarios"
        grid_param = [utils.Param(TB=f"{endpoint}.{query_field}", P=query_value)]
        res = await clients.IxcClient.get(endpoint=endpoint, grid_param=grid_param)
        regs = res.get("registros", [])
        login = regs[0] if regs else None

        return login

    @classmethod
    async def _get_device(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
    ) -> dict[str, Any] | None:
        """
        Retrieve the ACS device associated with an IXC login ID.

        Args:
            login_id (NonNegativeInt): IXC login ID used to locate the login and its ACS device.

        Returns:
            dict[str, Any] | None: First matching ACS device record, or None if the login or device cannot be found.
        """
        # --- Get login (IXC) ---
        login = await cls._get_login(login_id=login_id)

        if login is None:
            return None

        # --- Get device (ACS) ---
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
        regs = res.get("registers", [])
        device = regs[0] if regs else None

        return device

    @classmethod
    async def get_dns_server(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
    ) -> schemas.DnsServerOut:
        """
        Get the DNS server configured on the WAN PPP interface of a customer's ACS device.

        Args:
            login_id (NonNegativeInt): IXC login ID used to locate the customer's ACS device.

        Returns:
            schemas.DnsServerOut: DNS server configured on the first WAN PPP interface.

        Raises:
            HTTPException: 404 if the device does not exit; 404 if the WAN interface does not exist.
        """
        # --- Get device (ACS) ---
        device = await cls._get_device(login_id=login_id)

        if device is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo inexistente"
            )

        # --- Get WAN (ACS) ---
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
        Check whether a customer's ACS device reports IPv6 information.

        Args:
            login_id (NonNegativeInt): IXC login ID used to locate the customer's ACS device.

        Returns:
            schemas.HasIPV6OutSchema: Whether the device reports non-empty IPv6 information.

        Raises:
            HTTPException: 404 if the device does not exist; 404 if IPv6 device data cannot be found.
        """
        # --- Get device (ACS) ---
        device = await cls._get_device(login_id=login_id)

        if device is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo inexistente"
            )

        # --- Get device info (ACS) ---
        serial_number = device["serialNumber"]
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
                detail="Dados inexistentes",
            )
        info = regs[0]
        tem_ipv6 = bool(info["deviceInfo"]["ipv6"].split())

        return schemas.HasIPV6OutSchema(tem_ipv6=tem_ipv6)

    @classmethod
    async def get_uptime(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
    ) -> schemas.UptimeOutSchema:
        """
        Get the formatted uptime of a customer's ACS device.

        Args:
            login_id (NonNegativeInt): IXC login ID used to locate the customer's ACS device.

        Returns:
            schemas.UptimeOutSchema: Device uptime formatted as DD days, HH hours, MM minutes, and SS seconds.

        Raises:
            HTTPException: 404 if the device does not exist.
        """
        # --- Get device (ACS) ---
        device = await cls._get_device(login_id=login_id)

        if device is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo inexistente"
            )

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
        Get the RX and TX fiber signal values reported by a customer's ACS device.

        Args:
            login_id (NonNegativeInt): IXC login ID used to locate the customer's ACS device.

        Returns:
            schemas.FiberSignalOutSchema: RX and TX fiber signal values.

        Raises:
            HTTPException: 404 if the device does not exist.
        """
        # --- Get device (ACS) ---
        device = await cls._get_device(login_id=login_id)

        if device is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo inexistente"
            )

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
        List active customer contracts with pagination metadata.

        Args:
            protocol (str | None): Optional protocol filter.
            cnpj_cpf (str | None): Optional CNPJ/CPF filter.
            page (PositiveInt): Page number to retrieve.
            items_per_page (PositiveInt): Number of items per page.

        Returns:
            schemas.ListOutSchema[schemas.ContractOutSchema]: Contract records and pagination metadata.
        """
        # --- Get contracts (IXC) ---
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
        Get the connection status from an IXC login record.

        Args:
            login_id (NonNegativeInt): IXC login ID used to retrieve connection status.

        Returns:
            schemas.ConnectionStatusOutSchema: Connection status from the IXC login record.

        Raises:
            HTTPException: 404 if the login does not exist.
        """
        # --- Get login (IXC) ---
        login = await cls._get_login(login_id=login_id)

        if login is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Login inexistente"
            )

        return schemas.ConnectionStatusOutSchema(status_conexao=login["online"])

    @classmethod
    async def get_onu_status(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt | None = None,
        onu_mac: str | None = None,
    ) -> schemas.OnuStatusOutSchema:
        """
        Retrieve the ONU RX signal status by IXC login ID or ONU MAC address.

        Attempts to read the RX signal form the ACS device first; if unavailable,
        falls back to the IXC `radpop_radio_cliente_fibra` endpoint.

        Args:
            login_id (NonNegativeInt | None): IXC login ID used to locate the ONU.
                Optional (default: None).
            onu_mac (str | None): ONU MAC address used to locate the ONU.
                Optional (default: None)

        Returns:
            schemas.OnuStatusOutSchema: ONU RX signal and its computed status.

        Raises:
            HTTPException: 400 if neither `login_id` nor a valid `onu_mac` is provided;
                404 if the login, device, or ONU signal cannot be found.
        """
        ixc_endpoint = "radpop_radio_cliente_fibra"

        if login_id is not None:
            # --- Get device (ACS) ---
            device = await cls._get_device(login_id=login_id)

            if device is not None:
                rx_signal = device["deviceInfo"].get("rx")
                return schemas.OnuStatusOutSchema(sinal_rx=rx_signal)

            # --- Get ONU (IXC) ---
            grid_param = [utils.Param(TB=f"{ixc_endpoint}.id_login", P=login_id)]
            res = await clients.IxcClient.get(
                endpoint=ixc_endpoint, grid_param=grid_param
            )
            regs = res.get("registros", [])
            rx_signal = regs[0].get("sinal_rx") if regs else None
            if rx_signal is None or float(rx_signal) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Sinal inexistente"
                )
            return schemas.OnuStatusOutSchema(sinal_rx=rx_signal)
        elif (
            onu_mac is not None and onu_mac.strip()
        ) and not utils.OPA_PLACEHOLDER_RE.search(string=onu_mac) is not None:
            # --- Get login (IXC) ---
            login = await cls._get_login(onu_mac=onu_mac)

            if login is not None:
                # --- Get device (ACS) ---
                device = await cls._get_device(login_id=login["id"])

                if device is not None:
                    rx_signal = device["deviceInfo"].get("rx")
                    return schemas.OnuStatusOutSchema(sinal_rx=rx_signal)

            # --- Get ONU (IXC) ---
            grid_param = [utils.Param(TB=f"{ixc_endpoint}.mac", P=onu_mac)]
            res = await clients.IxcClient.get(
                endpoint=ixc_endpoint, grid_param=grid_param
            )
            regs = res.get("registros", [])
            rx_signal = regs[0].get("sinal_rx") if regs else None
            if rx_signal is None or float(rx_signal) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Sinal inexistente"
                )
            return schemas.OnuStatusOutSchema(sinal_rx=rx_signal)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça id_login ou mac_onu",
            )

    @classmethod
    async def post_disconnect_customer(
        cls,
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
    ) -> schemas.MessageOutSchema:
        """
        Disconnect a customer through IXC, falling back to an ACS reboot if needed.

        Args:
            login_id (NonNegativeInt): IXC login ID used to disconnect the customer.

        Returns:
            schemas.MessageOutSchema: Success message after disconnecting the customer.

        Raises:
            HTTPException: 404 if the ACS device does not exist when fallback is required; 500 if the ACS reboot fails.
        """
        # --- Post disconnect (IXC) ---
        res = await clients.IxcClient.post(
            endpoint="desconectar_clientes", payload={"id": login_id}
        )
        if res["msg"][0]["type"] == "success":  # "error" or "success"
            print("Customer disconnected through IXC")
            return schemas.MessageOutSchema(mensagem="Desconexão bem-sucedida")

        # --- Get device (ACS) ---
        device = await cls._get_device(login_id=login_id)
        if device is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo inexistente"
            )

        # --- Post disconnect (ACS) ---
        endpoint = f"devices/{device['serialNumber']}/reboot"
        res = await clients.IxcAcsClient.get(endpoint=endpoint)
        acs_message = res["message"]
        if "being rebooted" in acs_message:
            print("Customer disconnected through ACS")
            return schemas.MessageOutSchema(mensagem="Desconexão bem-sucedida")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=acs_message
        )

    @staticmethod
    async def get_tickets(
        # IDs NonNegativeInt, because IXC
        login_id: NonNegativeInt,
        page: PositiveInt,
        items_per_page: PositiveInt,
    ) -> schemas.ListOutSchema[schemas.TicketOutSchema]:
        """
        List non-finalized support tickets for an IXC login with pagination metadata.

        Args:
            login_id (NonNegativeInt): IXC login ID used to retrieve support tickets.
            page (PositiveInt): Page number to retrieve.
            items_per_page (PositiveInt): Number of items per page.

        Returns:
            schemas.ListOutSchema[schemas.TicketOutSchema]: Support ticket records and pagination metadata.
        """
        # --- Get tickets (IXC) ---
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
        Create a support ticket in IXC and return the created ticket.

        Args:
            ticket (schemas.TicketInSchema): Support ticket data to create.

        Returns:
            schemas.TicketOutSchema: Created support ticket.

        Raises:
            HTTPException: 500 if IXC does not return a created ticket ID.
        """
        # --- Post ticket (IXC) ---
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

        # --- Get ticket (IXC) ---
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
        Update the IP address and/or RADIUS pool for an IXC login.

        Args:
            login_id (NonNegativeInt): IXC login ID to update.
            ip (str | None): New IP address. Optional (default: None).
            pool_radius (str | None): New RADIUS pool. Optional (default: None).

        Returns:
            schemas.IpOutSchema: Updated IP address and RADIUS pool.

        Raises:
            HTTPException: 400 if neither IP nor RADIUS pool is provided; 404 if the login does not exist; 500 if the update fails.
        """
        if (ip is None or not ip.strip()) and (
            pool_radius is None or not pool_radius.strip()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forneça ip ou pool_radius",
            )

        # --- Get login (IXC) ---
        old_login = await cls._get_login(login_id=login_id)
        if old_login is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Login inexistente"
            )

        new_ip = ip if ip else old_login["ip"]
        new_radius = pool_radius if pool_radius else old_login["pool_radius"]
        updated_login: Any = {
            **old_login,
            "ip": new_ip or "",
            "pool_radius": new_radius or "",
        }
        del updated_login["id"]

        # --- Put login (IXC) ---
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
        Clear the MAC address associated with an IXC login.

        Args:
            login_id (NonNegativeInt): IXC login ID whose MAC address should be cleared.

        Returns:
            schemas.MessageOutSchema: Success message after clearing the MAC address.

        Raises:
            HTTPException: 500 if IXC returns an error, using a sanitized error message.
        """
        # --- Post clear mack (IXC) ---
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
        Get WIFI SSID and password data from an IXC login record.

        Args:
            login_id (NonNegativeInt): IXC login ID used to retrieve WiFi data.

        Returns:
            schemas.WifiOutSchema: 2.4 GHz and 5 GHz WiFi SSIDs and passwords.

        Raises:
            HTTPException: 404 if the login does not exist.
        """
        # --- Get login (IXC) ---
        login = await cls._get_login(login_id=login_id)
        if login is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Login inexistente"
            )

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
        Update WiFi SSID and/or password on an ACS device for both enabled 2.4 GHz and 5.8 GHz interfaces.

        Args:
            login_id (NonNegativeInt): IXC login ID used to locate the customer's ACS device.
            ssid (str | None): New SSID for the 2.4 GHz interface; the 5GHz SSID is set to this value with _5G suffix. Optional (default: None).
            ssid_pass (str | None): New WiFi password for both interfaces. Optional (default: None).

        Returns:
            schemas.MessageOutSchema: Success message after updating WiFi data.

        Raises:
            HTTPException: 404 if the device does not exist; 404 if WiFi data does not exist.
        """
        # --- Get device (ACS) ---
        device = await cls._get_device(login_id=login_id)
        if device is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo inexistente"
            )

        serial_number = device["serialNumber"]

        # --- Get wifi data (ACS) ---
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
        if ssid is not None and ssid.strip():
            payload_2g["ssid"] = ssid
            payload_5g["ssid"] = f"{ssid}_5G"
        if ssid_pass is not None and ssid_pass.strip():
            payload_2g["password"] = ssid_pass
            payload_5g["password"] = ssid_pass

        # --- Patch wifi data (ACS) ---
        await clients.IxcAcsClient.patch(
            endpoint=f"devices/{serial_number}/wifi/{interface_2g['id']}",
            payload=payload_2g,
        )
        await clients.IxcAcsClient.patch(
            endpoint=f"devices/{serial_number}/wifi/{interface_5g['id']}",
            payload=payload_5g,
        )

        return schemas.MessageOutSchema(mensagem="Atualização bem-sucedida")
