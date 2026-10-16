"""
Common FastAPI query parameter type aliases.
"""

from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from .. import db

# Protocol: attendance protocol
Protocol = Annotated[str, Query(description="Protocolo de atendimento")]
# CNPJ/CPF: customer document
CnpjCpf = Annotated[str, Query(description="CPF ou CNPJ do cliente")]
# Page: page number for pagination
Page = Annotated[int, Query(ge=1, description="Número da página")]
# ItemsPerPage: number of items per page
ItemsPerPage = Annotated[int, Query(ge=1, description="Itens por página")]
# LoginID: login ID associated to the customer (IDs NonNegativeInt, because IXC)
LoginID = Annotated[int, Query(ge=0, description="ID de login do cliente")]

# Db: current database session
DbDep = Annotated[AsyncSession, Depends(db.get_db)]
