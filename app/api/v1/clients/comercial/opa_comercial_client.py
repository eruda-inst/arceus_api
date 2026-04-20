from .. import opa_client


class ComercialOpaCliente(opa_client.OpaCliente):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    async def cliente_existe(cls, cpf_cnpj_limpo: str) -> bool:
        payload = {"filter": {"cpf_cnpj": cpf_cnpj_limpo}, "options": {"limit": 1}}
        data = await cls()._make_request(endpoint="cliente", payload=payload)
        if data.get("data"):
            return True
        return False
