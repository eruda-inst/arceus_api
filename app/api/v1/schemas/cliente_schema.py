from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class ClienteUpdate(BaseModel):
    ativo: Optional[str] = Field(
        default=None,
        description="Indica se o cliente está ativo. (S para Sim, N para Não).",
    )
    id_tipo_cliente: Optional[str] = Field(
        default=None, description="ID do tipo de cliente."
    )
    tipo_cliente_scm: Optional[str] = Field(
        default=None,
        description="Tipo de cliente SCM (Serviço de Comunicação Multimídia).",
    )
    tipo_ente_governamental: Optional[str] = Field(
        default=None, description="Tipo de ente governamental, se aplicável."
    )
    pais: Optional[str] = Field(default=None, description="País.")
    tipo_pessoa: Optional[str] = Field(
        default=None,
        description="Tipo de pessoa jurídica (F para Física, J para Jurídica).",
    )
    regime_fiscal_col: Optional[str] = Field(
        default=None, description="Coluna de regime fiscal."
    )
    razao: Optional[str] = Field(
        default=None, description="Razão social da empresa (para pessoas jurídicas)."
    )
    fantasia: Optional[str] = Field(
        default=None,
        description="Nome fantasia ou apelido da empresa (para pessoas jurídicas).",
    )
    tipo_documento_identificacao: Optional[str] = Field(
        default=None, description="Tipo de documento de identificação."
    )
    cnpj_cpf: Optional[str] = Field(
        default=None,
        description="CNPJ do cliente (para empresas) ou CPF (para pessoas físicas).",
    )
    ie_identidade: Optional[str] = Field(
        default=None, description="Inscrição Estadual ou Carteira de Identidade (RG)."
    )
    contribuinte_icms: Optional[str] = Field(
        default=None, description="Indica se o cliente é contribuinte do ICMS."
    )
    contribuinte_icms_alert: Optional[str] = Field(
        default=None,
        description="Alerta relacionado ao status de contribuinte do ICMS.",
    )
    rg_orgao_emissor: Optional[str] = Field(
        default=None, description="Órgão emissor da Carteira de Identidade (RG)."
    )
    nacionalidade: Optional[str] = Field(default=None, description="Nacionalidade.")
    cidade_naturalidade: Optional[str] = Field(
        default=None, description="Cidade de nascimento."
    )
    estado_nascimento: Optional[str] = Field(
        default=None, description="Estado de nascimento."
    )
    data_nascimento: Optional[str] = Field(
        default=None, description="Data de nascimento."
    )
    Sexo: Optional[str] = Field(default=None, description="Gênero.")
    profissao: Optional[str] = Field(default=None, description="Profissão.")
    estado_civil: Optional[str] = Field(default=None, description="Estado civil.")
    inscricao_municipal: Optional[str] = Field(
        default=None, description="Inscrição Municipal."
    )
    isuf: Optional[str] = Field(default=None, description="Número de registro ISUF.")
    tipo_assinante: Optional[str] = Field(
        default=None, description="Tipo de assinante."
    )
    filial_id: Optional[str] = Field(default=None, description="ID da filial.")
    filtra_filial: Optional[str] = Field(
        default=None, description="Filtrar por filial."
    )
    idx: Optional[str] = Field(default=None, description="ID principal do cliente.")
    data_cadastro: Optional[str] = Field(default=None, description="Data de cadastro.")
    ativo_serasa: Optional[str] = Field(
        default=None, description="Indica se está ativo no Serasa."
    )
    convert_cliente_forn: Optional[str] = Field(
        default=None, description="Converter cliente em fornecedor."
    )
    atualizar_cadastro_galaxPay: Optional[str] = Field(
        default=None, description="Atualizar cadastro no GalaxPay."
    )
    grau_satisfacao: Optional[str] = Field(
        default=None, description="Nível de satisfação do cliente."
    )
    id_condominio: Optional[str] = Field(
        default=None, description="ID do condomínio, se aplicável."
    )
    bloco: Optional[str] = Field(
        default=None, description="Bloco do edifício (para condomínios)."
    )
    apartamento: Optional[str] = Field(
        default=None, description="Número do apartamento (para condomínios)."
    )
    cep: Optional[str] = Field(default=None, description="CEP do endereço principal.")
    cif: Optional[str] = Field(
        default=None, description="Informações CIF (Custo, Seguro e Frete)."
    )
    endereco: Optional[str] = Field(
        default=None, description="Endereço da rua principal."
    )
    numero: Optional[str] = Field(
        default=None, description="Número do endereço principal."
    )
    complemento: Optional[str] = Field(
        default=None, description="Complemento do endereço principal (ex: apto, sala)."
    )
    bairro: Optional[str] = Field(
        default=None, description="Bairro do endereço principal."
    )
    cidade: Optional[str] = Field(
        default=None, description="Cidade do endereço principal."
    )
    uf: Optional[str] = Field(
        default=None, description="Estado do endereço principal (UF)."
    )
    referencia: Optional[str] = Field(
        default=None, description="Ponto de referência do endereço principal."
    )
    moradia: Optional[str] = Field(
        default=None, description="Tipo de residência (ex: Casa, Apartamento)."
    )
    tipo_localidade: Optional[str] = Field(
        default=None, description="Tipo de localidade (ex: Urbana, Rural)."
    )
    latitude: Optional[str] = Field(default=None, description="Latitude do endereço.")
    longitude: Optional[str] = Field(default=None, description="Longitude do endereço.")
    cep_cob: Optional[str] = Field(
        default=None, description="CEP do endereço de cobrança."
    )
    endereco_cob: Optional[str] = Field(
        default=None, description="Endereço de cobrança."
    )
    numero_cob: Optional[str] = Field(
        default=None, description="Número do endereço de cobrança."
    )
    bairro_cob: Optional[str] = Field(
        default=None, description="Bairro do endereço de cobrança."
    )
    cidade_cob: Optional[str] = Field(
        default=None, description="Cidade do endereço de cobrança."
    )
    complemento_cob: Optional[str] = Field(
        default=None, description="Complemento do endereço de cobrança."
    )
    referencia_cob: Optional[str] = Field(
        default=None, description="Ponto de referência do endereço de cobrança."
    )
    uf_cob: Optional[str] = Field(
        default=None, description="Estado do endereço de cobrança (UF)."
    )
    fone: Optional[str] = Field(default=None, description="Telefone principal.")
    telefone_comercial: Optional[str] = Field(
        default=None, description="Telefone comercial."
    )
    ramal: Optional[str] = Field(default=None, description="Ramal telefônico.")
    id_operadora_celular: Optional[str] = Field(
        default=None, description="ID da operadora de celular."
    )
    telefone_celular: Optional[str] = Field(
        default=None, description="Número de telefone celular."
    )
    whatsapp: Optional[str] = Field(default=None, description="Número do WhatsApp.")
    email: Optional[str] = Field(
        default=None, description="Endereço de e-mail principal."
    )
    contato: Optional[str] = Field(
        default=None, description="Nome da pessoa de contato principal."
    )
    website: Optional[str] = Field(default=None, description="URL do site.")
    skype: Optional[str] = Field(default=None, description="ID do Skype.")
    facebook: Optional[str] = Field(
        default=None, description="URL do perfil do Facebook."
    )
    hotsite_email: Optional[str] = Field(
        default=None, description="Endereço de e-mail do hotsite."
    )
    senha: Optional[str] = Field(
        default=None, description="Senha para o portal do cliente."
    )
    acesso_automatico_central: Optional[str] = Field(
        default=None, description="Habilitar login automático no portal do cliente."
    )
    alterar_senha_primeiro_acesso: Optional[str] = Field(
        default=None, description="Forçar alteração de senha no primeiro login."
    )
    senha_hotsite_md5: Optional[str] = Field(
        default=None, description="Hash MD5 da senha do hotsite."
    )
    hotsite_acesso: Optional[str] = Field(
        default=None, description="Habilitar acesso ao hotsite."
    )
    crm: Optional[str] = Field(
        default=None, description="Informações relacionadas ao CRM."
    )
    id_segmento: Optional[str] = Field(
        default=None, description="ID do segmento do CRM."
    )
    id_candato_tipo: Optional[str] = Field(
        default=None, description="ID do tipo de candidato do CRM."
    )
    id_campanha: Optional[str] = Field(
        default=None, description="ID da campanha do CRM."
    )
    id_concorrente: Optional[str] = Field(
        default=None, description="ID do concorrente do CRM."
    )
    id_perfil: Optional[str] = Field(default=None, description="ID do perfil do CRM.")
    responsavel: Optional[str] = Field(
        default=None, description="Pessoa responsável pela conta do cliente."
    )
    indicado_por: Optional[str] = Field(
        default=None, description="Quem indicou o cliente."
    )
    cadastrado_via_viabilidade: Optional[str] = Field(
        default=None, description="Cadastrado através de verificação de viabilidade."
    )
    status_prospeccao: Optional[str] = Field(
        default=None, description="Status de prospecção."
    )
    crm_data_novo: Optional[str] = Field(
        default=None, description="Data em que o status mudou para 'Novo'."
    )
    crm_data_sondagem: Optional[str] = Field(
        default=None, description="Data em que o status mudou para 'Sondagem'."
    )
    crm_data_apresentando: Optional[str] = Field(
        default=None, description="Data em que o status mudou para 'Apresentando'."
    )
    crm_data_negociando: Optional[str] = Field(
        default=None, description="Data em que o status mudou para 'Negociando'."
    )
    crm_data_vencemos: Optional[str] = Field(
        default=None, description="Data em que o status mudou para 'Ganhamos'."
    )
    crm_data_perdemos: Optional[str] = Field(
        default=None, description="Data em que o status mudou para 'Perdemos'."
    )
    crm_data_abortamos: Optional[str] = Field(
        default=None, description="Data em que o status mudou para 'Abortado'."
    )
    crm_data_sem_porta_disponivel: Optional[str] = Field(
        default=None,
        description="Data em que o status mudou para 'Sem Porta Disponível'.",
    )
    crm_data_sem_viabilidade: Optional[str] = Field(
        default=None, description="Data em que o status mudou para 'Sem Viabilidade'."
    )
    pipe_id_organizacao: Optional[str] = Field(
        default=None, description="ID da organização no Pipedrive."
    )
    foto_cartao: Optional[str] = Field(
        default=None, description="Foto de um cartão (ex: cartão de visita)."
    )
    participa_cobranca: Optional[str] = Field(
        default=None,
        description="Indica se o cliente está incluído em processos de cobrança.",
    )
    num_dias_cob: Optional[str] = Field(
        default=None, description="Número de dias para cobrança."
    )
    participa_pre_cobranca: Optional[str] = Field(
        default=None,
        description="Indica se o cliente está incluído em processos de pré-cobrança.",
    )
    cob_envia_email: Optional[str] = Field(
        default=None, description="Enviar notificações de cobrança por e-mail."
    )
    cob_envia_sms: Optional[str] = Field(
        default=None, description="Enviar notificações de cobrança por SMS."
    )
    fieldset_mensagem_atencao_regua_crm: Optional[str] = Field(
        default=None, description="Mensagem de atenção para regra de cobrança do CRM."
    )
    id_conta: Optional[str] = Field(
        default=None, description="ID da conta bancária para cobrança."
    )
    cond_pagamento: Optional[str] = Field(
        default=None, description="Condição de pagamento."
    )
    id_vendedor: Optional[str] = Field(default=None, description="ID do vendedor.")
    tabela_preco: Optional[str] = Field(
        default=None, description="ID da tabela de preços."
    )
    deb_automatico: Optional[str] = Field(
        default=None, description="Habilitar débito automático."
    )
    deb_agencia: Optional[str] = Field(
        default=None, description="Agência bancária para débito automático."
    )
    deb_conta: Optional[str] = Field(
        default=None, description="Conta bancária para débito automático."
    )
    codigo_operacao: Optional[str] = Field(
        default=None, description="Código de operação para débito automático."
    )
    tipo_pessoa_titular_conta: Optional[str] = Field(
        default=None, description="Tipo de pessoa do titular da conta (F/J)."
    )
    cnpj_cpf_titular_conta: Optional[str] = Field(
        default=None, description="CNPJ/CPF do titular da conta."
    )
    ultima_atualizacao: Optional[str] = Field(
        default=None, description="Data da última atualização."
    )
    regua_cobranca_considera: Optional[str] = Field(
        default=None, description="Considerar para regra de cobrança."
    )
    regua_cobranca_wpp: Optional[str] = Field(
        default=None, description="Usar WhatsApp para regra de cobrança."
    )
    regua_cobranca_notificacao: Optional[str] = Field(
        default=None, description="Usar notificação para regra de cobrança."
    )
    fieldset_mensagem_atencao_regua: Optional[str] = Field(
        default=None, description="Mensagem de atenção para regra de cobrança."
    )
    nome_pai: Optional[str] = Field(default=None, description="Nome do pai.")
    cpf_pai: Optional[str] = Field(default=None, description="CPF do pai.")
    identidade_pai: Optional[str] = Field(
        default=None, description="Carteira de identidade do pai."
    )
    nascimento_pai: Optional[str] = Field(
        default=None, description="Data de nascimento do pai."
    )
    nome_mae: Optional[str] = Field(default=None, description="Nome da mãe.")
    cpf_mae: Optional[str] = Field(default=None, description="CPF da mãe.")
    identidade_mae: Optional[str] = Field(
        default=None, description="Carteira de identidade da mãe."
    )
    nascimento_mae: Optional[str] = Field(
        default=None, description="Data de nascimento da mãe."
    )
    quantidade_dependentes: Optional[str] = Field(
        default=None, description="Número de dependentes."
    )
    nome_conjuge: Optional[str] = Field(default=None, description="Nome do cônjuge.")
    fone_conjuge: Optional[str] = Field(
        default=None, description="Telefone do cônjuge."
    )
    cpf_conjuge: Optional[str] = Field(default=None, description="CPF do cônjuge.")
    rg_conjuge: Optional[str] = Field(
        default=None, description="Carteira de identidade (RG) do cônjuge."
    )
    data_nascimento_conjuge: Optional[str] = Field(
        default=None, description="Data de nascimento do cônjuge."
    )
    nome_contador: Optional[str] = Field(default=None, description="Nome do contador.")
    telefone_contador: Optional[str] = Field(
        default=None, description="Telefone do contador."
    )
    orgao_publico: Optional[str] = Field(
        default=None, description="Indica se é um órgão público."
    )
    im: Optional[str] = Field(default=None, description="Inscrição Municipal.")
    nome_representante_1: Optional[str] = Field(
        default=None, description="Nome do representante legal 1."
    )
    cpf_representante_1: Optional[str] = Field(
        default=None, description="CPF do representante legal 1."
    )
    identidade_representante_1: Optional[str] = Field(
        default=None, description="Carteira de identidade do representante legal 1."
    )
    nome_representante_2: Optional[str] = Field(
        default=None, description="Nome do representante legal 2."
    )
    cpf_representante_2: Optional[str] = Field(
        default=None, description="CPF do representante legal 2."
    )
    identidade_representante_2: Optional[str] = Field(
        default=None, description="Carteira de identidade do representante legal 2."
    )
    emp_empresa: Optional[str] = Field(
        default=None, description="Nome da empresa empregadora."
    )
    emp_cnpj: Optional[str] = Field(
        default=None, description="CNPJ da empresa empregadora."
    )
    emp_cep: Optional[str] = Field(
        default=None, description="CEP da empresa empregadora."
    )
    emp_endereco: Optional[str] = Field(
        default=None, description="Endereço da empresa empregadora."
    )
    emp_cidade: Optional[str] = Field(
        default=None, description="Cidade da empresa empregadora."
    )
    emp_fone: Optional[str] = Field(
        default=None, description="Telefone da empresa empregadora."
    )
    emp_cargo: Optional[str] = Field(default=None, description="Cargo/função.")
    emp_remuneracao: Optional[str] = Field(
        default=None, description="Salário/remuneração."
    )
    emp_data_admissao: Optional[str] = Field(
        default=None, description="Data de admissão na empresa."
    )
    iss_classificacao_padrao: Optional[str] = Field(
        default=None, description="Classificação padrão do ISS."
    )
    pis_retem: Optional[str] = Field(default=None, description="Reter PIS.")
    cofins_retem: Optional[str] = Field(default=None, description="Reter COFINS.")
    csll_retem: Optional[str] = Field(default=None, description="Reter CSLL.")
    irrf_retem: Optional[str] = Field(default=None, description="Reter IRRF.")
    desconto_irrf_valor_inferior: Optional[str] = Field(
        default=None, description="Desconto de IRRF para valor inferior."
    )
    inss_retem: Optional[str] = Field(default=None, description="Reter INSS.")
    cli_desconta_iss_retido_total: Optional[str] = Field(
        default=None, description="Cliente desconta total de ISS retido."
    )
    dica_imposto_retido_cliente: Optional[str] = Field(
        default=None, description="Dica sobre imposto retido pelo cliente."
    )
    percentual_reducao: Optional[str] = Field(
        default=None, description="Percentual de redução."
    )
    ref_com_empresa1: Optional[str] = Field(
        default=None, description="Referência comercial 1: nome da empresa."
    )
    ref_com_fone1: Optional[str] = Field(
        default=None, description="Referência comercial 1: telefone."
    )
    ref_com_empresa2: Optional[str] = Field(
        default=None, description="Referência comercial 2: nome da empresa."
    )
    ref_com_fone2: Optional[str] = Field(
        default=None, description="Referência comercial 2: telefone."
    )
    ref_pes_nome1: Optional[str] = Field(
        default=None, description="Referência pessoal 1: nome."
    )
    ref_pes_fone1: Optional[str] = Field(
        default=None, description="Referência pessoal 1: telefone."
    )
    ref_pes_nome2: Optional[str] = Field(
        default=None, description="Referência pessoal 2: nome."
    )
    ref_pes_fone2: Optional[str] = Field(
        default=None, description="Referência pessoal 2: telefone."
    )
    obs: Optional[str] = Field(default=None, description="Observações gerais.")
    alerta: Optional[str] = Field(
        default=None, description="Mensagem de alerta para o cliente."
    )
