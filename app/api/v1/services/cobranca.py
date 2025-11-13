from . import service
from typing import Self, Optional
from .. import utils, schemas, clients
from fastapi import HTTPException, status
from pydantic import ValidationError, PositiveInt


class CobrancaService(service.Service):
    """
    Serviço para encapsular a lógica de negócios relacionada às operações de cobrança.
    """
