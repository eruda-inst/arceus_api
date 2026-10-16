"""
Router for triage endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Body

from .. import schemas, services, utils

triage_router = APIRouter(prefix="/triagem", tags=["Triagem"])


@triage_router.get(
    path="/contato-cliente", summary="Obtém dados de contato de um cliente"
)
async def get_customer_contact(
    protocolo: utils.Protocol | None = None,
    cnpj_cpf: utils.CnpjCpf | None = None,
) -> schemas.ContactOutSchema:
    """
    Obtém dados de contato de um cliente, através do protocolo de atendimento ou CPF/CNPJ
    """
    return await services.TriageService.get_customer_contact(
        protocol=protocolo, cnpj_cpf=cnpj_cpf
    )


@triage_router.patch(path="/contato-cliente", summary="Atualiza contato de um cliente")
async def patch_customer_contact(
    telefone_celular: Annotated[
        str, Body(embed=True, description="Novo telefone celular")
    ],
    protocolo: utils.Protocol | None = None,
    cnpj_cpf: utils.CnpjCpf | None = None,
) -> schemas.ContactOutSchema:
    """
    Atualiza contato de um cliente, através do protocolo de atendimento ou CPF/CNPJ
    """
    return await services.TriageService.patch_customer_contact(
        protocol=protocolo, cnpj_cpf=cnpj_cpf, phone_number=telefone_celular
    )
