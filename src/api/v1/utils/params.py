"""
Common FastAPI query parameter type aliases.
"""

from typing import Annotated

from fastapi import Query

# Protocol: 12-character attendance protocol
Protocol = Annotated[
    str,
    Query(min_length=12, max_length=12, description="Protocolo de atendimento"),
]
# CNPJ/CPF: customer document
CnpjCpf = Annotated[str, Query(description="CPF ou CNPJ do cliente")]
# Page: page number for pagination
Page = Annotated[int, Query(ge=1, description="Número da página")]
# ItemsPerPage: number of items per page
ItemsPerPage = Annotated[int, Query(ge=1, description="Itens por página")]
