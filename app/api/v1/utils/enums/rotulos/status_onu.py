from enum import Enum


class StatusONURot(str, Enum):
    SATURADO = "Saturado"
    EXCELENTE = "Excelente"
    BOM = "Bom"
    REGULAR = "Regular"
    RUIM = "Ruim"
    PESSIMO = "Péssimo"
    SEM_ONU = "Sem ONU"
