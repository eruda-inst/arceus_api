from . import service_service
from datetime import datetime
from typing import Optional, Any
from .. import utils, schemas, clients
from fastapi import HTTPException, status
from pydantic import ValidationError, PositiveInt


class ComercialService(service_service.Service):
    def __init__(self) -> None:
        super().__init__()
        self.comercial_ixc_cliente = clients.ComercialIXCCliente()
        self.suporte_ixc_cliente = clients.SuporteIXCCliente()

    async def get_status_acesso(
        self, id_contrato: PositiveInt
    ) -> schemas.StatusAcessoOut:
        try:
            res = await self.comercial_ixc_cliente.get_status_acesso(
                id_contrato=id_contrato
            )
            status_acesso = res.get("registros", [])
            if not status_acesso:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sem status de acesso.",
                )
            status_acesso_cod = status_acesso[0].get("status_internet")
            status_acesso_rot = utils.rotular_status_acesso(
                status_acesso_codigo=status_acesso_cod
            )
            return schemas.StatusAcessoOut(
                data=schemas.StatusAcesso(status_acesso=status_acesso_rot)
            )
        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Validação da resposta falhou: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    async def get_contratos(
        self,
        protocolo: Optional[str] = None,
        cnpj_cpf: Optional[str] = None,
        page: Optional[PositiveInt] = 1,
        per_page: Optional[PositiveInt] = 10,
        sortname: Optional[str] = "cliente_contrato.id",
        sortorder: Optional[utils.SortOrder] = utils.SortOrder.ASC,
    ) -> schemas.ComercialContratoListOut:
        try:
            id_cliente = await self.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )

            res = await self.comercial_ixc_cliente.get_contratos(
                id_cliente=id_cliente,
                page=page,
                per_page=per_page,
                sortname=sortname,
                sortorder=sortorder,
            )
            if not res.get("registros", []):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Sem contrato."
                )
            contratos = res["registros"]

            contratos_tratados: Any = []
            hoje = datetime.now().date()

            for contrato in contratos:
                a_receber_res = (
                    await self.comercial_ixc_cliente.get_valor_e_data_vencimento(
                        id_contrato=contrato["id"]
                    )
                )
                titulos_nao_quitados = [
                    ar
                    for ar in a_receber_res.get("registros", [])
                    if ar.get("status") != "Q"
                ]

                if not titulos_nao_quitados:
                    login = await self.comercial_ixc_cliente.get_login(
                        id_cliente=contrato["id_cliente"]
                    )

                    if not login.get("registros"):
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND, detail="Sem login."
                        )

                    contrato_tratado: Any = {
                        "id": contrato["id"],
                        "contrato": contrato["contrato"],
                        "valor": 0.00,
                        "status_acesso": utils.rotular_status_acesso(
                            status_acesso_codigo=contrato["status_internet"]
                        ),
                        "data_vencimento": "N/A",
                        "id_cliente": contrato["id_cliente"],
                        "id_login": login.get("registros")[0]["id"],
                    }
                    contratos_tratados.append(contrato_tratado)
                    continue

                proximo_vencimento = None
                menor_diferenca = None

                for titulo in titulos_nao_quitados:
                    data_vencimento_str = titulo.get("data_vencimento")
                    if data_vencimento_str:
                        try:
                            data_vencimento = datetime.strptime(
                                data_vencimento_str, "%Y-%m-%d"
                            ).date()
                            diferenca = (data_vencimento - hoje).days

                            if diferenca >= 0 and (
                                menor_diferenca is None or diferenca < menor_diferenca
                            ):
                                menor_diferenca = diferenca
                                proximo_vencimento = titulo
                        except ValueError:
                            continue

                titulo_final = proximo_vencimento
                if not titulo_final:
                    titulo_final = max(
                        titulos_nao_quitados,
                        key=lambda x: datetime.strptime(
                            x.get("data_vencimento"), "%Y-%m-%d"
                        ).date(),
                    )

                login = await self.comercial_ixc_cliente.get_login(
                    id_cliente=contrato["id_cliente"]
                )

                if not login.get("registros"):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Sem login."
                    )

                contrato_tratado = {
                    "id": contrato["id"],
                    "contrato": contrato["contrato"],
                    "valor": titulo_final.get("valor", 0.00),
                    "status_acesso": utils.rotular_status_acesso(
                        status_acesso_codigo=contrato["status_internet"]
                    ),
                    "data_vencimento": titulo_final.get("data_vencimento", "N/A"),
                    "id_cliente": contrato["id_cliente"],
                    "id_login": login.get("registros")[0]["id"],
                }
                contratos_tratados.append(contrato_tratado)

            total = int(res.get("total", 0))

            meta = schemas.Meta(
                total=total,
                page=page,
                per_page=per_page,
            )

            return schemas.ComercialContratoListOut(
                data=[schemas.ComercialContrato(**ct) for ct in contratos_tratados],
                meta=meta,
            )

        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Validação da resposta falhou: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    async def post_leads(self, lead: schemas.LeadIn) -> schemas.LeadCreate:
        try:
            lead_data = lead.model_dump()
            if lead_data.get("cnpj_cpf"):
                cnpj_cpf = lead_data["cnpj_cpf"]
                lead_data["cnpj_cpf"] = utils.formatar_cnpj_cpf(cnpj_cpf=cnpj_cpf)
            if lead_data.get("fone_whatsapp"):
                cel = lead_data["fone_whatsapp"]
                lead_data["fone_whatsapp"] = utils.formatar_cel(cel=cel)
            if lead_data.get("fone_celular"):
                cel = lead_data["fone_celular"]
                lead_data["fone_celular"] = utils.formatar_cel(cel=cel)
            if lead_data.get("cep"):
                cep = lead_data["cep"]
                lead_data["cep"] = utils.formatar_cep(cep=cep)
            if lead_data.get("data_nascimento"):
                data_nascimento = lead_data["data_nascimento"]
                lead_data["data_nascimento"] = utils.formatar_data(data=data_nascimento)

            formatted_lead = schemas.LeadIn(**lead_data)

            res = await self.comercial_ixc_cliente.post_leads(lead=formatted_lead)

            id_lead = res.get("id", None)
            if not id_lead:
                error_message = res.get("message", "")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Não foi possível retornar o ID do lead criado: {error_message}",
                )
            return schemas.LeadCreate(id=id_lead)
        except HTTPException:
            raise
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Validação da resposta falhou: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    @staticmethod
    async def cliente_existe(cpf_cnpj: str) -> schemas.ClienteExisteOut:
        try:
            cpf_cnpj_limpo = utils.limpar_string(cpf_cnpj)
            cliente_existe = await clients.ComercialOpaCliente.cliente_existe(
                cpf_cnpj_limpo=cpf_cnpj_limpo
            )
            return schemas.ClienteExisteOut(cliente_existe=cliente_existe)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )
