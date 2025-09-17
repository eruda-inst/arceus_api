from enum import Enum


class OrigemEnderecoCod(str, Enum):
    CLIENTE = "C"
    LOGIN = "L"
    CONTRATO = "CC"
    MANUAL = "M"