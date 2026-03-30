from enum import StrEnum


class StatusONURot(StrEnum):
    SATURADO = "Saturado"
    EXCELENTE = "Excelente"
    BOM = "Bom"
    REGULAR = "Regular"
    RUIM = "Ruim"
    PESSIMO = "Péssimo"
    SEM_ONU = "Sem ONU"
