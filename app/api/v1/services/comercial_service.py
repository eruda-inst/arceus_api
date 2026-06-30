from typing import Any
from . import service_service
from pydantic import PositiveInt
from fastapi import HTTPException, status
from .. import utils, schemas, clients, services


class ComercialService(service_service.Service):
    @staticmethod
    async def get_status_acesso(id_contrato: PositiveInt) -> schemas.StatusAcessoOut:
        try:
            endpoint = "cliente_contrato"
            grid_param = [
                {"TB": "cliente_contrato.id", "OP": "=", "P": str(id_contrato)}
            ]
            res = await clients.IXCCliente.get(endpoint=endpoint, grid_param=grid_param)
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
            return schemas.StatusAcessoOut(status_acesso=status_acesso_rot)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    @classmethod
    async def get_contratos(
        cls,
        protocolo: str | None = None,
        cnpj_cpf: str | None = None,
        page: PositiveInt | None = 1,
        per_page: PositiveInt | None = 10,
    ):
        try:
            # --- Cliente ---
            id_cliente = await cls.get_id_cliente_ixc(
                protocolo=protocolo, cnpj_cpf=cnpj_cpf
            )
            res = await clients.IXCCliente.get_cliente_ixc(id=id_cliente)
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Nenum cliente encontrado.",
                )
            cliente = regs[0]

            # --- Contratos ---
            endpoint = "cliente_contrato"
            grid_param = [
                {"TB": "cliente_contrato.id_cliente", "OP": "=", "P": str(id_cliente)},
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "I"},
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "N"},
                {"TB": "cliente_contrato.status", "OP": "!=", "P": "D"},
            ]
            res = await clients.IXCCliente.get(
                endpoint=endpoint, grid_param=grid_param, page=page, per_page=per_page
            )
            regs = res.get("registros", [])
            if not regs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Nenhum contrato encontrado.",
                )
            total = res.get("total", 0)
            contratos = regs

            contratos_parciais: list[schemas.ComercialContrato] = []

            # --- Iteração entre contratos ---
            for contrato in contratos:
                id_contrato = contrato.get("id")

                # --- Login ---
                endpoint = "radusuarios"
                grid_param = [
                    {"TB": "radusuarios.id_contrato", "OP": "=", "P": str(id_contrato)}
                ]
                res = await clients.IXCCliente.get(
                    endpoint=endpoint, grid_param=grid_param
                )
                regs = res.get("registros", [])
                if not regs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Nenhum login encontrado.",
                    )
                login = regs[0]

                # --- Proxima fatura aberta ---
                proxima_fatura_aberta = (
                    await services.FinanceiroService.get_proxima_fatura_aberta(
                        id_contrato=id_contrato
                    )
                )

                if not proxima_fatura_aberta:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Nenhuma fatura aberta encontrada.",
                    )

                # --- Contrato parcial ---
                contratos_parciais.append(
                    schemas.ComercialContrato(
                        id=id_contrato,
                        contrato=contrato.get("contrato"),
                        nome_cliente=cliente.get("razao"),
                        valor=proxima_fatura_aberta["valor"],
                        status_acesso=utils.rotular_status_acesso(
                            status_acesso_codigo=contrato.get("status_internet")
                        ),
                        data_vencimento=proxima_fatura_aberta["data_vencimento"],
                        id_cliente=id_cliente,
                        id_login=login.get("id"),
                    )
                )

            return schemas.ComercialContratoListOut(
                data=contratos_parciais,
                meta=schemas.Meta(total=total, page=page, per_page=per_page),
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {e}",
            )

    @staticmethod
    async def post_leads(lead: schemas.LeadIn) -> schemas.LeadCreate:
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

            """
            Este campo "data_cadastro" é obrigatório na API do IXC (temos que mandar alguma coisa), porém o que é mandado é descartado e a data é gerada automaticamente pela própria API deles.

            Só mais uma esquisitice da API do IXC.
            """
            endpoint = "contato"
            payload = formatted_lead.model_dump()
            payload["data_cadastro"] = "N/A"
            res = await clients.IXCCliente.post(endpoint=endpoint, payload=payload)

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
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    @staticmethod
    async def cliente_existe(cpf_cnpj: str) -> schemas.ClienteExisteOut:
        try:
            cpf_cnpj_limpo = utils.limpar_string(cpf_cnpj)
            cliente_existe = await clients.OpaCliente.cliente_existe(
                cpf_cnpj_limpo=cpf_cnpj_limpo
            )
            return schemas.ClienteExisteOut(cliente_existe=cliente_existe)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )

    @staticmethod
    async def put_lead(cnpj_cpf: str, lead: schemas.LeadUpdate) -> schemas.LeadOut:
        try:
            # 1. Buscar lead existente pelo CNPJ/CPF
            endpoint = "contato"
            grid_param = [
                {
                    "TB": "contato.cnpj_cpf",
                    "OP": "=",
                    "P": utils.formatar_cnpj_cpf(cnpj_cpf),
                }
            ]
            response = await clients.IXCCliente.get(
                endpoint=endpoint, grid_param=grid_param
            )
            registros = response.get("registros", [])
            if not registros:
                raise HTTPException(
                    status.HTTP_404_NOT_FOUND, detail="Lead não encontrado."
                )

            lead_antigo = registros[0]
            lead_id = lead_antigo["id"]

            # 2. Mesclar dados antigos com os novos (excluindo None)
            dados_atualizados: Any = {
                **lead_antigo,
                **lead.model_dump(exclude_none=True),
            }
            # Remove campos que não devem ser enviados (ex: o próprio id, data_cadastro etc.)
            dados_atualizados.pop("id", None)

            # 3. Aplicar formatações (igual ao post_leads)
            if dados_atualizados.get("cnpj_cpf"):
                dados_atualizados["cnpj_cpf"] = utils.formatar_cnpj_cpf(
                    cnpj_cpf=dados_atualizados["cnpj_cpf"]
                )
            if dados_atualizados.get("fone_whatsapp"):
                dados_atualizados["fone_whatsapp"] = utils.formatar_cel(
                    cel=dados_atualizados["fone_whatsapp"]
                )
            if dados_atualizados.get("fone_celular"):
                dados_atualizados["fone_celular"] = utils.formatar_cel(
                    cel=dados_atualizados["fone_celular"]
                )
            if dados_atualizados.get("cep"):
                dados_atualizados["cep"] = utils.formatar_cep(
                    cep=dados_atualizados["cep"]
                )
            if dados_atualizados.get("data_nascimento"):
                dados_atualizados["data_nascimento"] = utils.formatar_data(
                    data=dados_atualizados["data_nascimento"]
                )

            # 4. Chamar o método de atualização no cliente
            id = lead_id
            endpoint = "contato"
            payload = dados_atualizados
            await clients.IXCCliente.put(endpoint=endpoint, id=id, payload=payload)

            return schemas.LeadOut(**dados_atualizados)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno ao processar solicitação: {str(e)}",
            )
