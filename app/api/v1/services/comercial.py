from typing import Self
from ..clients import IXCClient, OpaClient


class Service:
    def __init__(
        self: Self,
    ) -> None:
        self.opa_client = OpaClient()
        self.ixc_client = IXCClient()

    async def get_status_acesso():
        pass