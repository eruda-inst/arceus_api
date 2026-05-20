from pydantic import BaseModel, Field


class ClienteUpdate(BaseModel):
    ativo: str | None = Field(
        default=None,
        description="Indica se o cliente está ativo. (S para Sim, N para Não).",
    )
    id_tipo_cliente: str | None = Field(
        default=None, description="ID do tipo de cliente."
    )
    tipo_cliente_scm: str | None = Field(
        default=None,
        description="Tipo de cliente SCM (Serviço de Comunicação Multimídia).",
    )
    tipo_ente_governamental: str | None = Field(
        default=None, description="Tipo de ente governamental, se aplicável."
    )
    pais: str | None = Field(default=None, description="País.")
    tipo_pessoa: str | None = Field(
        default=None,
        description="Tipo de pessoa jurídica (F para Física, J para Jurídica).",
    )
    regime_fiscal_col: str | None = Field(
        default=None, description="Coluna de regime fiscal."
    )
    razao: str | None = Field(
        default=None, description="Razão social da empresa (para pessoas jurídicas)."
    )
    fantasia: str | None = Field(
        default=None,
        description="Nome fantasia ou apelido da empresa (para pessoas jurídicas).",
    )
    tipo_documento_identificacao: str | None = Field(
        default=None, description="Tipo de documento de identificação."
    )
    cnpj_cpf: str | None = Field(
        default=None,
        description="CNPJ do cliente (para empresas) ou CPF (para pessoas físicas).",
    )
    ie_identidade: str | None = Field(
        default=None, description="Inscrição Estadual ou Carteira de Identidade (RG)."
    )
    contribuinte_icms: str | None = Field(
        default=None, description="Indica se o cliente é contribuinte do ICMS."
    )
    contribuinte_icms_alert: str | None = Field(
        default=None,
        description="Alerta relacionado ao status de contribuinte do ICMS.",
    )
    rg_orgao_emissor: str | None = Field(
        default=None, description="Órgão emissor da Carteira de Identidade (RG)."
    )
    nacionalidade: str | None = Field(default=None, description="Nacionalidade.")
    cidade_naturalidade: str | None = Field(
        default=None, description="Cidade de nascimento."
    )
    estado_nascimento: str | None = Field(
        default=None, description="Estado de nascimento."
    )
    data_nascimento: str | None = Field(default=None, description="Data de nascimento.")
    Sexo: str | None = Field(default=None, description="Gênero.")
    profissao: str | None = Field(default=None, description="Profissão.")
    estado_civil: str | None = Field(default=None, description="Estado civil.")
    inscricao_municipal: str | None = Field(
        default=None, description="Inscrição Municipal."
    )
    isuf: str | None = Field(default=None, description="Número de registro ISUF.")
    tipo_assinante: str | None = Field(default=None, description="Tipo de assinante.")
    filial_id: str | None = Field(default=None, description="ID da filial.")
    filtra_filial: str | None = Field(default=None, description="Filtrar por filial.")
    idx: str | None = Field(default=None, description="ID principal do cliente.")
    data_cadastro: str | None = Field(default=None, description="Data de cadastro.")
    ativo_serasa: str | None = Field(
        default=None, description="Indica se está ativo no Serasa."
    )
    convert_cliente_forn: str | None = Field(
        default=None, description="Converter cliente em fornecedor."
    )
    atualizar_cadastro_galaxPay: str | None = Field(
        default=None, description="Atualizar cadastro no GalaxPay."
    )
    grau_satisfacao: str | None = Field(
        default=None, description="Nível de satisfação do cliente."
    )
    id_condominio: str | None = Field(
        default=None, description="ID do condomínio, se aplicável."
    )
    bloco: str | None = Field(
        default=None, description="Bloco do edifício (para condomínios)."
    )
    apartamento: str | None = Field(
        default=None, description="Número do apartamento (para condomínios)."
    )
    cep: str | None = Field(default=None, description="CEP do endereço principal.")
    cif: str | None = Field(
        default=None, description="Informações CIF (Custo, Seguro e Frete)."
    )
    endereco: str | None = Field(default=None, description="Endereço da rua principal.")
    numero: str | None = Field(
        default=None, description="Número do endereço principal."
    )
    complemento: str | None = Field(
        default=None, description="Complemento do endereço principal (ex: apto, sala)."
    )
    bairro: str | None = Field(
        default=None, description="Bairro do endereço principal."
    )
    cidade: str | None = Field(
        default=None, description="Cidade do endereço principal."
    )
    uf: str | None = Field(
        default=None, description="Estado do endereço principal (UF)."
    )
    referencia: str | None = Field(
        default=None, description="Ponto de referência do endereço principal."
    )
    moradia: str | None = Field(
        default=None, description="Tipo de residência (ex: Casa, Apartamento)."
    )
    tipo_localidade: str | None = Field(
        default=None, description="Tipo de localidade (ex: Urbana, Rural)."
    )
    latitude: str | None = Field(default=None, description="Latitude do endereço.")
    longitude: str | None = Field(default=None, description="Longitude do endereço.")
    cep_cob: str | None = Field(
        default=None, description="CEP do endereço de cobrança."
    )
    endereco_cob: str | None = Field(default=None, description="Endereço de cobrança.")
    numero_cob: str | None = Field(
        default=None, description="Número do endereço de cobrança."
    )
    bairro_cob: str | None = Field(
        default=None, description="Bairro do endereço de cobrança."
    )
    cidade_cob: str | None = Field(
        default=None, description="Cidade do endereço de cobrança."
    )
    complemento_cob: str | None = Field(
        default=None, description="Complemento do endereço de cobrança."
    )
    referencia_cob: str | None = Field(
        default=None, description="Ponto de referência do endereço de cobrança."
    )
    uf_cob: str | None = Field(
        default=None, description="Estado do endereço de cobrança (UF)."
    )
    fone: str | None = Field(default=None, description="Telefone principal.")
    telefone_comercial: str | None = Field(
        default=None, description="Telefone comercial."
    )
    ramal: str | None = Field(default=None, description="Ramal telefônico.")
    id_operadora_celular: str | None = Field(
        default=None, description="ID da operadora de celular."
    )
    telefone_celular: str | None = Field(
        default=None, description="Número de telefone celular."
    )
    whatsapp: str | None = Field(default=None, description="Número do WhatsApp.")
    email: str | None = Field(default=None, description="Endereço de e-mail principal.")
    contato: str | None = Field(
        default=None, description="Nome da pessoa de contato principal."
    )
    website: str | None = Field(default=None, description="URL do site.")
    skype: str | None = Field(default=None, description="ID do Skype.")
    facebook: str | None = Field(default=None, description="URL do perfil do Facebook.")
    hotsite_email: str | None = Field(
        default=None, description="Endereço de e-mail do hotsite."
    )
    senha: str | None = Field(
        default=None, description="Senha para o portal do cliente."
    )
    acesso_automatico_central: str | None = Field(
        default=None, description="Habilitar login automático no portal do cliente."
    )
    alterar_senha_primeiro_acesso: str | None = Field(
        default=None, description="Forçar alteração de senha no primeiro login."
    )
    senha_hotsite_md5: str | None = Field(
        default=None, description="Hash MD5 da senha do hotsite."
    )
    hotsite_acesso: str | None = Field(
        default=None, description="Habilitar acesso ao hotsite."
    )
    crm: str | None = Field(
        default=None, description="Informações relacionadas ao CRM."
    )
    id_segmento: str | None = Field(default=None, description="ID do segmento do CRM.")
    id_candato_tipo: str | None = Field(
        default=None, description="ID do tipo de candidato do CRM."
    )
    id_campanha: str | None = Field(default=None, description="ID da campanha do CRM.")
    id_concorrente: str | None = Field(
        default=None, description="ID do concorrente do CRM."
    )
    id_perfil: str | None = Field(default=None, description="ID do perfil do CRM.")
    responsavel: str | None = Field(
        default=None, description="Pessoa responsável pela conta do cliente."
    )
    indicado_por: str | None = Field(
        default=None, description="Quem indicou o cliente."
    )
    cadastrado_via_viabilidade: str | None = Field(
        default=None, description="Cadastrado através de verificação de viabilidade."
    )
    status_prospeccao: str | None = Field(
        default=None, description="Status de prospecção."
    )
    crm_data_novo: str | None = Field(
        default=None, description="Data em que o status mudou para 'Novo'."
    )
    crm_data_sondagem: str | None = Field(
        default=None, description="Data em que o status mudou para 'Sondagem'."
    )
    crm_data_apresentando: str | None = Field(
        default=None, description="Data em que o status mudou para 'Apresentando'."
    )
    crm_data_negociando: str | None = Field(
        default=None, description="Data em que o status mudou para 'Negociando'."
    )
    crm_data_vencemos: str | None = Field(
        default=None, description="Data em que o status mudou para 'Ganhamos'."
    )
    crm_data_perdemos: str | None = Field(
        default=None, description="Data em que o status mudou para 'Perdemos'."
    )
    crm_data_abortamos: str | None = Field(
        default=None, description="Data em que o status mudou para 'Abortado'."
    )
    crm_data_sem_porta_disponivel: str | None = Field(
        default=None,
        description="Data em que o status mudou para 'Sem Porta Disponível'.",
    )
    crm_data_sem_viabilidade: str | None = Field(
        default=None, description="Data em que o status mudou para 'Sem Viabilidade'."
    )
    pipe_id_organizacao: str | None = Field(
        default=None, description="ID da organização no Pipedrive."
    )
    foto_cartao: str | None = Field(
        default=None, description="Foto de um cartão (ex: cartão de visita)."
    )
    participa_cobranca: str | None = Field(
        default=None,
        description="Indica se o cliente está incluído em processos de cobrança.",
    )
    num_dias_cob: str | None = Field(
        default=None, description="Número de dias para cobrança."
    )
    participa_pre_cobranca: str | None = Field(
        default=None,
        description="Indica se o cliente está incluído em processos de pré-cobrança.",
    )
    cob_envia_email: str | None = Field(
        default=None, description="Enviar notificações de cobrança por e-mail."
    )
    cob_envia_sms: str | None = Field(
        default=None, description="Enviar notificações de cobrança por SMS."
    )
    fieldset_mensagem_atencao_regua_crm: str | None = Field(
        default=None, description="Mensagem de atenção para regra de cobrança do CRM."
    )
    id_conta: str | None = Field(
        default=None, description="ID da conta bancária para cobrança."
    )
    cond_pagamento: str | None = Field(
        default=None, description="Condição de pagamento."
    )
    id_vendedor: str | None = Field(default=None, description="ID do vendedor.")
    tabela_preco: str | None = Field(
        default=None, description="ID da tabela de preços."
    )
    deb_automatico: str | None = Field(
        default=None, description="Habilitar débito automático."
    )
    deb_agencia: str | None = Field(
        default=None, description="Agência bancária para débito automático."
    )
    deb_conta: str | None = Field(
        default=None, description="Conta bancária para débito automático."
    )
    codigo_operacao: str | None = Field(
        default=None, description="Código de operação para débito automático."
    )
    tipo_pessoa_titular_conta: str | None = Field(
        default=None, description="Tipo de pessoa do titular da conta (F/J)."
    )
    cnpj_cpf_titular_conta: str | None = Field(
        default=None, description="CNPJ/CPF do titular da conta."
    )
    ultima_atualizacao: str | None = Field(
        default=None, description="Data da última atualização."
    )
    regua_cobranca_considera: str | None = Field(
        default=None, description="Considerar para regra de cobrança."
    )
    regua_cobranca_wpp: str | None = Field(
        default=None, description="Usar WhatsApp para regra de cobrança."
    )
    regua_cobranca_notificacao: str | None = Field(
        default=None, description="Usar notificação para regra de cobrança."
    )
    fieldset_mensagem_atencao_regua: str | None = Field(
        default=None, description="Mensagem de atenção para regra de cobrança."
    )
    nome_pai: str | None = Field(default=None, description="Nome do pai.")
    cpf_pai: str | None = Field(default=None, description="CPF do pai.")
    identidade_pai: str | None = Field(
        default=None, description="Carteira de identidade do pai."
    )
    nascimento_pai: str | None = Field(
        default=None, description="Data de nascimento do pai."
    )
    nome_mae: str | None = Field(default=None, description="Nome da mãe.")
    cpf_mae: str | None = Field(default=None, description="CPF da mãe.")
    identidade_mae: str | None = Field(
        default=None, description="Carteira de identidade da mãe."
    )
    nascimento_mae: str | None = Field(
        default=None, description="Data de nascimento da mãe."
    )
    quantidade_dependentes: str | None = Field(
        default=None, description="Número de dependentes."
    )
    nome_conjuge: str | None = Field(default=None, description="Nome do cônjuge.")
    fone_conjuge: str | None = Field(default=None, description="Telefone do cônjuge.")
    cpf_conjuge: str | None = Field(default=None, description="CPF do cônjuge.")
    rg_conjuge: str | None = Field(
        default=None, description="Carteira de identidade (RG) do cônjuge."
    )
    data_nascimento_conjuge: str | None = Field(
        default=None, description="Data de nascimento do cônjuge."
    )
    nome_contador: str | None = Field(default=None, description="Nome do contador.")
    telefone_contador: str | None = Field(
        default=None, description="Telefone do contador."
    )
    orgao_publico: str | None = Field(
        default=None, description="Indica se é um órgão público."
    )
    im: str | None = Field(default=None, description="Inscrição Municipal.")
    nome_representante_1: str | None = Field(
        default=None, description="Nome do representante legal 1."
    )
    cpf_representante_1: str | None = Field(
        default=None, description="CPF do representante legal 1."
    )
    identidade_representante_1: str | None = Field(
        default=None, description="Carteira de identidade do representante legal 1."
    )
    nome_representante_2: str | None = Field(
        default=None, description="Nome do representante legal 2."
    )
    cpf_representante_2: str | None = Field(
        default=None, description="CPF do representante legal 2."
    )
    identidade_representante_2: str | None = Field(
        default=None, description="Carteira de identidade do representante legal 2."
    )
    emp_empresa: str | None = Field(
        default=None, description="Nome da empresa empregadora."
    )
    emp_cnpj: str | None = Field(
        default=None, description="CNPJ da empresa empregadora."
    )
    emp_cep: str | None = Field(default=None, description="CEP da empresa empregadora.")
    emp_endereco: str | None = Field(
        default=None, description="Endereço da empresa empregadora."
    )
    emp_cidade: str | None = Field(
        default=None, description="Cidade da empresa empregadora."
    )
    emp_fone: str | None = Field(
        default=None, description="Telefone da empresa empregadora."
    )
    emp_cargo: str | None = Field(default=None, description="Cargo/função.")
    emp_remuneracao: str | None = Field(
        default=None, description="Salário/remuneração."
    )
    emp_data_admissao: str | None = Field(
        default=None, description="Data de admissão na empresa."
    )
    iss_classificacao_padrao: str | None = Field(
        default=None, description="Classificação padrão do ISS."
    )
    pis_retem: str | None = Field(default=None, description="Reter PIS.")
    cofins_retem: str | None = Field(default=None, description="Reter COFINS.")
    csll_retem: str | None = Field(default=None, description="Reter CSLL.")
    irrf_retem: str | None = Field(default=None, description="Reter IRRF.")
    desconto_irrf_valor_inferior: str | None = Field(
        default=None, description="Desconto de IRRF para valor inferior."
    )
    inss_retem: str | None = Field(default=None, description="Reter INSS.")
    cli_desconta_iss_retido_total: str | None = Field(
        default=None, description="Cliente desconta total de ISS retido."
    )
    dica_imposto_retido_cliente: str | None = Field(
        default=None, description="Dica sobre imposto retido pelo cliente."
    )
    percentual_reducao: str | None = Field(
        default=None, description="Percentual de redução."
    )
    ref_com_empresa1: str | None = Field(
        default=None, description="Referência comercial 1: nome da empresa."
    )
    ref_com_fone1: str | None = Field(
        default=None, description="Referência comercial 1: telefone."
    )
    ref_com_empresa2: str | None = Field(
        default=None, description="Referência comercial 2: nome da empresa."
    )
    ref_com_fone2: str | None = Field(
        default=None, description="Referência comercial 2: telefone."
    )
    ref_pes_nome1: str | None = Field(
        default=None, description="Referência pessoal 1: nome."
    )
    ref_pes_fone1: str | None = Field(
        default=None, description="Referência pessoal 1: telefone."
    )
    ref_pes_nome2: str | None = Field(
        default=None, description="Referência pessoal 2: nome."
    )
    ref_pes_fone2: str | None = Field(
        default=None, description="Referência pessoal 2: telefone."
    )
    obs: str | None = Field(default=None, description="Observações gerais.")
    alerta: str | None = Field(
        default=None, description="Mensagem de alerta para o cliente."
    )
