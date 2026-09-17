from typing import Annotated

from fastapi import Query

Protocol = Annotated[
    str,
    Query(min_length=12, max_length=12, description="Protocolo de atendimento"),
]
CnpjCpf = Annotated[str, Query(description="CPF ou CNPJ do cliente")]
Page = Annotated[int, Query(ge=1, description="Número da página")]
ItemsPerPage = Annotated[int, Query(ge=1, description="Itens por página")]
