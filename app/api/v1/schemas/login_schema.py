from pydantic import BaseModel, Field


class LoginUpdate(BaseModel):
    autenticacao: str | None = Field(
        default="L",
        description="Tipo de autenticação.",
    )
    tipo_conexao_mapa: str | None = Field(
        default=None,
        description="Tipo de conexão do mapa.",
    )
    id_integracao: str | None = Field(default=None, description="ID de integração.")
    lte_id: str | None = Field(default=None, description="ID LTE.")
    pacote_lte: str | None = Field(default=None, description="Pacote LTE.")
    id_cliente: str | None = Field(default=None, description="ID do cliente.")
    id_contrato: str | None = Field(default=None, description="ID do contrato.")
    id_filial: str | None = Field(default=None, description="ID da filial.")
    contrato_plano_venda_: str | None = Field(
        default=None, description="Contrato plano venda."
    )
    id_grupo: str | None = Field(default=None, description="ID do grupo.")
    login: str | None = Field(default=None, description="Login do usuário.")
    agent_circuit_id: str | None = Field(default=None, description="Agent Circuit ID.")
    senha_md5: str | None = Field(
        default="N", description="Indica se senha está em MD5."
    )
    senha: str | None = Field(default=None, description="Senha do usuário.")
    ping_traceroute: str | None = Field(default=None, description="Ping e traceroute.")
    ativo: str | None = Field(default="S", description="Indica se está ativo.")
    online: str | None = Field(default="SS", description="Status online.")
    login_simultaneo: str | None = Field(
        default="1", description="Número de logins simultâneos."
    )
    ultima_atualizacao: str | None = Field(
        default="CURRENT_TIMESTAMP", description="Data da última atualização."
    )
    usuario_router1: str | None = Field(
        default=None, description="Usuário do router 1."
    )
    senha_router1: str | None = Field(default=None, description="Senha do router 1.")
    senha_router2: str | None = Field(default=None, description="Senha do router 2.")
    ssid_router_wifi: str | None = Field(
        default=None, description="SSID do router WiFi."
    )
    senha_rede_sem_fio: str | None = Field(
        default=None, description="Senha da rede sem fio."
    )
    ssid_router_wifi_5ghz: str | None = Field(
        default=None, description="SSID do router WiFi 5GHz."
    )
    senha_rede_sem_fio_5ghz: str | None = Field(
        default=None, description="Senha da rede sem fio 5GHz."
    )
    redirect_interfaces: str | None = Field(
        default=None, description="Redirecionamento de interfaces."
    )
    ip: str | None = Field(default=None, description="Endereço IP.")
    ip_aviso: str | None = Field(default=None, description="IP para aviso.")
    auto_preencher_ip: str | None = Field(default="H", description="Auto preencher IP.")
    fixar_ip: str | None = Field(default="H", description="Fixar IP.")
    relacionar_ip_ao_login: str | None = Field(
        default="H", description="Relacionar IP ao login."
    )
    framed_pd_ipv6: str | None = Field(default=None, description="Framed PD IPv6.")
    framed_autopreencher_ipv6: str | None = Field(
        default="H", description="Framed auto preencher IPv6."
    )
    framed_fixar_ipv6: str | None = Field(default="H", description="Framed fixar IPv6.")
    framed_relacionar_ipv6_ao_login: str | None = Field(
        default="H", description="Framed relacionar IPv6 ao login."
    )
    pd_ipv6: str | None = Field(default=None, description="PD IPv6.")
    auto_preencher_ipv6: str | None = Field(
        default="H", description="Auto preencher IPv6."
    )
    fixar_ipv6: str | None = Field(default="H", description="Fixar IPv6.")
    relacionar_ipv6_ao_login: str | None = Field(
        default="H", description="Relacionar IPv6 ao login."
    )
    mac: str | None = Field(default=None, description="Endereço MAC.")
    autenticacao_por_mac: str | None = Field(
        default="P", description="Autenticação por MAC."
    )
    usuario_wpa2aes: str | None = Field(default=None, description="Usuário WPA2 AES.")
    senha_wpa2aes: str | None = Field(default=None, description="Senha WPA2 AES.")
    autenticacao_wpa: str | None = Field(default=None, description="Autenticação WPA.")
    id_porta_transmissor: str | None = Field(
        default=None, description="ID da porta do transmissor."
    )
    auto_preencher_mac: str | None = Field(
        default="H", description="Auto preencher MAC."
    )
    relacionar_mac_ao_login: str | None = Field(
        default="H", description="Relacionar MAC ao login."
    )
    relacionar_concentrador_ao_login: str | None = Field(
        default="H", description="Relacionar concentrador ao login."
    )
    pool_radius: str | None = Field(default=None, description="Pool RADIUS.")
    id_radgrupos_pools: str | None = Field(
        default=None, description="ID dos grupos de pools RADIUS."
    )
    id_rad_dns: str | None = Field(default=None, description="ID RAD DNS.")
    id_concentrador: str | None = Field(default=None, description="ID do concentrador.")
    ip_concentrador: str | None = Field(default=None, description="IP do concentrador.")
    interface: str | None = Field(default=None, description="Interface de rede.")
    vlan: str | None = Field(default=None, description="VLAN.")
    vlan_ip_rede: str | None = Field(default=None, description="IP da rede VLAN.")
    gw_vlan: str | None = Field(default=None, description="Gateway da VLAN.")
    service_tag_vlan: str | None = Field(default="S", description="Service tag VLAN.")
    mtu: str | None = Field(default="1500", description="MTU.")
    concentrador: str | None = Field(default=None, description="Concentrador.")
    conexao: str | None = Field(default=None, description="Conexão.")
    tipo_conexao: str | None = Field(default=None, description="Tipo de conexão.")
    porta_http_nas: str | None = Field(default=None, description="Porta HTTP NAS.")
    acct_session_id: str | None = Field(
        default=None, description="ID da sessão accounting."
    )
    tipo_vinculo_plano: str | None = Field(
        default="D", description="Tipo de vínculo do plano."
    )
    cliente_tem_a_senha: str | None = Field(
        default="S", description="Cliente tem a senha."
    )
    autenticacao_wps: str | None = Field(default="S", description="Autenticação WPS.")
    autenticacao_mac: str | None = Field(default="S", description="Autenticação MAC.")
    tipo_acesso: str | None = Field(default="http", description="Tipo de acesso.")
    porta_http: str | None = Field(default=None, description="Porta HTTP.")
    porta_router2: str | None = Field(default=None, description="Porta do router 2.")
    ip_aux: str | None = Field(default=None, description="IP auxiliar.")
    porta_aux: str | None = Field(default=None, description="Porta auxiliar.")
    ultima_conexao_inicial: str | None = Field(
        default=None, description="Última conexão inicial."
    )
    ultima_conexao_final: str | None = Field(
        default=None, description="Última conexão final."
    )
    motivo_desconexao: str | None = Field(
        default=None, description="Motivo da desconexão."
    )
    count_desconexao: str | None = Field(
        default=None, description="Contador de desconexões."
    )
    tempo_conexao: str | None = Field(default=None, description="Tempo de conexão.")
    tempo_conectado: str | None = Field(default=None, description="Tempo conectado.")
    download_atual: str | None = Field(default=None, description="Download atual.")
    upload_atual: str | None = Field(default=None, description="Upload atual.")
    franquia_maximo: str | None = Field(default=None, description="Franquia máxima.")
    franquia_consumo: str | None = Field(
        default=None, description="Consumo da franquia."
    )
    franquia_consumo_up: str | None = Field(
        default=None, description="Consumo de upload da franquia."
    )
    franquia_atingida: str | None = Field(default="N", description="Franquia atingida.")
    onu_compartilhada: str | None = Field(
        default=None, description="ONU compartilhada."
    )
    id_df_projeto: str | None = Field(default=None, description="ID do projeto DF.")
    id_transmissor: str | None = Field(default=None, description="ID do transmissor.")
    modelo_tranmissor: str | None = Field(
        default=None, description="Modelo do transmissor."
    )
    interface_transmissao: str | None = Field(
        default=None, description="Interface de transmissão."
    )
    interface_transmissao_fibra: str | None = Field(
        default=None, description="Interface de transmissão fibra."
    )
    id_caixa_ftth: str | None = Field(default=None, description="ID da caixa FTTH.")
    ftth_porta: str | None = Field(default=None, description="Porta FTTH.")
    tronco: str | None = Field(default=None, description="Tronco.")
    splitter: str | None = Field(default=None, description="Splitter.")
    onu_mac: str | None = Field(default=None, description="MAC da ONU.")
    sinal_ultimo_atendimento: str | None = Field(
        default=None, description="Sinal do último atendimento."
    )
    id_hardware: str | None = Field(default=None, description="ID do hardware.")
    tipo_equipamento: str | None = Field(
        default=None, description="Tipo de equipamento."
    )
    metragem_interna: str | None = Field(default=None, description="Metragem interna.")
    metragem_externa: str | None = Field(default=None, description="Metragem externa.")
    id_reserva_rede_neutra: str | None = Field(
        default=None, description="ID da reserva da rede neutra."
    )
    endereco_padrao_cliente: str | None = Field(
        default="S", description="Endereço padrão do cliente."
    )
    ponta: str | None = Field(default=None, description="Ponta.")
    id_condominio: str | None = Field(default=None, description="ID do condomínio.")
    id_predio: str | None = Field(default=None, description="ID do prédio.")
    condominio_novo: str | None = Field(default=None, description="Condomínio novo.")
    bloco: str | None = Field(default=None, description="Bloco.")
    bloco_novo: str | None = Field(default=None, description="Bloco novo.")
    apartamento: str | None = Field(default=None, description="Apartamento.")
    apartamento_novo: str | None = Field(default=None, description="Apartamento novo.")
    cep: str | None = Field(default=None, description="CEP.")
    cep_novo: str | None = Field(default=None, description="CEP novo.")
    endereco: str | None = Field(default=None, description="Endereço.")
    endereco_novo: str | None = Field(default=None, description="Endereço novo.")
    numero: str | None = Field(default=None, description="Número.")
    numero_novo: str | None = Field(default=None, description="Número novo.")
    bairro: str | None = Field(default=None, description="Bairro.")
    bairro_novo: str | None = Field(default=None, description="Bairro novo.")
    cidade: str | None = Field(default=None, description="Cidade.")
    cidade_novo: str | None = Field(default=None, description="Cidade novo.")
    referencia: str | None = Field(default=None, description="Referência.")
    referencia_novo: str | None = Field(default=None, description="Referência nova.")
    complemento: str | None = Field(default=None, description="Complemento.")
    complemento_novo: str | None = Field(default=None, description="Complemento novo.")
    latitude: str | None = Field(default=None, description="Latitude.")
    latitude_novo: str | None = Field(default=None, description="Latitude nova.")
    longitude: str | None = Field(default=None, description="Longitude.")
    longitude_novo: str | None = Field(default=None, description="Longitude nova.")
    obs: str | None = Field(default=None, description="Observações.")
