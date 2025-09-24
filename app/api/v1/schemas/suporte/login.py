from typing import Optional
from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    autenticacao: Optional[str] = Field(
        default="L", description="Tipo de autenticação."
    )
    tipo_conexao_mapa: Optional[str] = Field(
        default=None, description="Tipo de conexão do mapa."
    )
    id_integracao: Optional[int] = Field(
        default=None, ge=1, description="ID de integração."
    )
    lte_id: Optional[int] = Field(default=None, ge=1, description="ID LTE.")
    pacote_lte: Optional[str] = Field(default=None, description="Pacote LTE.")
    id_cliente: Optional[int] = Field(default=None, ge=1, description="ID do cliente.")
    id_contrato: Optional[int] = Field(
        default=None, ge=1, description="ID do contrato."
    )
    id_filial: Optional[int] = Field(default=None, ge=1, description="ID da filial.")
    contrato_plano_venda_: Optional[str] = Field(
        default=None, description="Contrato plano venda."
    )
    id_grupo: Optional[int] = Field(default=None, ge=1, description="ID do grupo.")
    login: Optional[str] = Field(default=None, description="Login do usuário.")
    agent_circuit_id: Optional[int] = Field(
        default=None, description="Agent Circuit ID."
    )
    senha_md5: Optional[str] = Field(
        default="N", description="Indica se senha está em MD5."
    )
    senha: Optional[str] = Field(default=None, description="Senha do usuário.")
    ping_traceroute: Optional[str] = Field(
        default=None, description="Ping e traceroute."
    )
    ativo: Optional[str] = Field(default="S", description="Indica se está ativo.")
    online: Optional[str] = Field(default="SS", description="Status online.")
    login_simultaneo: Optional[int] = Field(
        default=1, ge=1, description="Número de logins simultâneos."
    )
    ultima_atualizacao: Optional[str] = Field(
        default="CURRENT_TIMESTAMP", description="Data da última atualização."
    )
    usuario_router1: Optional[str] = Field(
        default=None, description="Usuário do router 1."
    )
    senha_router1: Optional[str] = Field(default=None, description="Senha do router 1.")
    senha_router2: Optional[str] = Field(default=None, description="Senha do router 2.")
    ssid_router_wifi: Optional[str] = Field(
        default=None, description="SSID do router WiFi."
    )
    senha_rede_sem_fio: Optional[str] = Field(
        default=None, description="Senha da rede sem fio."
    )
    ssid_router_wifi_5ghz: Optional[str] = Field(
        default=None, description="SSID do router WiFi 5GHz."
    )
    senha_rede_sem_fio_5ghz: Optional[str] = Field(
        default=None, description="Senha da rede sem fio 5GHz."
    )
    redirect_interfaces: Optional[str] = Field(
        default=None, description="Redirecionamento de interfaces."
    )
    ip: Optional[str] = Field(default=None, description="Endereço IP.")
    ip_aviso: Optional[str] = Field(default=None, description="IP para aviso.")
    auto_preencher_ip: Optional[str] = Field(
        default="H", description="Auto preencher IP."
    )
    fixar_ip: Optional[str] = Field(default="H", description="Fixar IP.")
    relacionar_ip_ao_login: Optional[str] = Field(
        default="H", description="Relacionar IP ao login."
    )
    framed_pd_ipv6: Optional[str] = Field(default=None, description="Framed PD IPv6.")
    framed_autopreencher_ipv6: Optional[str] = Field(
        default="H", description="Framed auto preencher IPv6."
    )
    framed_fixar_ipv6: Optional[str] = Field(
        default="H", description="Framed fixar IPv6."
    )
    framed_relacionar_ipv6_ao_login: Optional[str] = Field(
        default="H", description="Framed relacionar IPv6 ao login."
    )
    pd_ipv6: Optional[str] = Field(default=None, description="PD IPv6.")
    auto_preencher_ipv6: Optional[str] = Field(
        default="H", description="Auto preencher IPv6."
    )
    fixar_ipv6: Optional[str] = Field(default="H", description="Fixar IPv6.")
    relacionar_ipv6_ao_login: Optional[str] = Field(
        default="H", description="Relacionar IPv6 ao login."
    )
    mac: Optional[str] = Field(default=None, description="Endereço MAC.")
    autenticacao_por_mac: Optional[str] = Field(
        default="P", description="Autenticação por MAC."
    )
    usuario_wpa2aes: Optional[str] = Field(
        default=None, description="Usuário WPA2 AES."
    )
    senha_wpa2aes: Optional[str] = Field(default=None, description="Senha WPA2 AES.")
    autenticacao_wpa: Optional[str] = Field(
        default=None, description="Autenticação WPA."
    )
    id_porta_transmissor: Optional[int] = Field(
        default=None, ge=1, description="ID da porta do transmissor."
    )
    auto_preencher_mac: Optional[str] = Field(
        default="H", description="Auto preencher MAC."
    )
    relacionar_mac_ao_login: Optional[str] = Field(
        default="H", description="Relacionar MAC ao login."
    )
    relacionar_concentrador_ao_login: Optional[str] = Field(
        default="H", description="Relacionar concentrador ao login."
    )
    pool_radius: Optional[int] = Field(default=None, description="Pool RADIUS.")
    id_radgrupos_pools: Optional[int] = Field(
        default=None, ge=1, description="ID dos grupos de pools RADIUS."
    )
    id_rad_dns: Optional[int] = Field(default=None, ge=1, description="ID RAD DNS.")
    id_concentrador: Optional[int] = Field(
        default=None, ge=1, description="ID do concentrador."
    )
    ip_concentrador: Optional[str] = Field(
        default=None, description="IP do concentrador."
    )
    interface: Optional[str] = Field(default=None, description="Interface de rede.")
    vlan: Optional[int] = Field(default=None, ge=1, description="VLAN.")
    vlan_ip_rede: Optional[str] = Field(default=None, description="IP da rede VLAN.")
    gw_vlan: Optional[str] = Field(default=None, description="Gateway da VLAN.")
    service_tag_vlan: Optional[str] = Field(
        default="S", description="Service tag VLAN."
    )
    mtu: Optional[int] = Field(default=1500, ge=1, description="MTU.")
    concentrador: Optional[str] = Field(default=None, description="Concentrador.")
    conexao: Optional[str] = Field(default=None, description="Conexão.")
    tipo_conexao: Optional[str] = Field(default=None, description="Tipo de conexão.")
    porta_http_nas: Optional[int] = Field(
        default=None, ge=1, description="Porta HTTP NAS."
    )
    acct_session_id: Optional[str] = Field(
        default=None, description="ID da sessão accounting."
    )
    tipo_vinculo_plano: Optional[str] = Field(
        default="D", description="Tipo de vínculo do plano."
    )
    cliente_tem_a_senha: Optional[str] = Field(
        default="S", description="Cliente tem a senha."
    )
    autenticacao_wps: Optional[str] = Field(
        default="S", description="Autenticação WPS."
    )
    autenticacao_mac: Optional[str] = Field(
        default="S", description="Autenticação MAC."
    )
    tipo_acesso: Optional[str] = Field(default="http", description="Tipo de acesso.")
    porta_http: Optional[int] = Field(default=None, ge=1, description="Porta HTTP.")
    porta_router2: Optional[int] = Field(
        default=None, ge=1, description="Porta do router 2."
    )
    ip_aux: Optional[int] = Field(default=None, description="IP auxiliar.")
    porta_aux: Optional[int] = Field(default=None, ge=1, description="Porta auxiliar.")
    ultima_conexao_inicial: Optional[str] = Field(
        default=None, description="Última conexão inicial."
    )
    ultima_conexao_final: Optional[str] = Field(
        default=None, description="Última conexão final."
    )
    motivo_desconexao: Optional[str] = Field(
        default=None, description="Motivo da desconexão."
    )
    count_desconexao: Optional[int] = Field(
        default=None, ge=1, description="Contador de desconexões."
    )
    tempo_conexao: Optional[int] = Field(
        default=None, ge=1, description="Tempo de conexão."
    )
    tempo_conectado: Optional[int] = Field(
        default=None, ge=1, description="Tempo conectado."
    )
    download_atual: Optional[int] = Field(
        default=None, ge=1, description="Download atual."
    )
    upload_atual: Optional[int] = Field(default=None, ge=1, description="Upload atual.")
    franquia_maximo: Optional[int] = Field(
        default=None, ge=1, description="Franquia máxima."
    )
    franquia_consumo: Optional[int] = Field(
        default=None, ge=1, description="Consumo da franquia."
    )
    franquia_consumo_up: Optional[int] = Field(
        default=None, ge=1, description="Consumo de upload da franquia."
    )
    franquia_atingida: Optional[str] = Field(
        default="N", description="Franquia atingida."
    )
    onu_compartilhada: Optional[str] = Field(
        default=None, description="ONU compartilhada."
    )
    id_df_projeto: Optional[int] = Field(
        default=None, ge=1, description="ID do projeto DF."
    )
    id_transmissor: Optional[int] = Field(
        default=None, ge=1, description="ID do transmissor."
    )
    modelo_tranmissor: Optional[str] = Field(
        default=None, description="Modelo do transmissor."
    )
    interface_transmissao: Optional[str] = Field(
        default=None, description="Interface de transmissão."
    )
    interface_transmissao_fibra: Optional[str] = Field(
        default=None, description="Interface de transmissão fibra."
    )
    id_caixa_ftth: Optional[int] = Field(
        default=None, ge=1, description="ID da caixa FTTH."
    )
    ftth_porta: Optional[int] = Field(default=None, ge=1, description="Porta FTTH.")
    tronco: Optional[str] = Field(default=None, description="Tronco.")
    splitter: Optional[str] = Field(default=None, description="Splitter.")
    onu_mac: Optional[str] = Field(default=None, description="MAC da ONU.")
    sinal_ultimo_atendimento: Optional[int] = Field(
        default=None, ge=1, description="Sinal do último atendimento."
    )
    id_hardware: Optional[int] = Field(
        default=None, ge=1, description="ID do hardware."
    )
    tipo_equipamento: Optional[str] = Field(
        default=None, description="Tipo de equipamento."
    )
    metragem_interna: Optional[int] = Field(
        default=None, ge=1, description="Metragem interna."
    )
    metragem_externa: Optional[int] = Field(
        default=None, ge=1, description="Metragem externa."
    )
    id_reserva_rede_neutra: Optional[int] = Field(
        default=None, ge=1, description="ID da reserva da rede neutra."
    )
    endereco_padrao_cliente: Optional[str] = Field(
        default="S", description="Endereço padrão do cliente."
    )
    ponta: Optional[str] = Field(default=None, description="Ponta.")
    id_condominio: Optional[int] = Field(
        default=None, ge=1, description="ID do condomínio."
    )
    id_predio: Optional[int] = Field(default=None, ge=1, description="ID do prédio.")
    condominio_novo: Optional[str] = Field(default=None, description="Condomínio novo.")
    bloco: Optional[str] = Field(default=None, description="Bloco.")
    bloco_novo: Optional[str] = Field(default=None, description="Bloco novo.")
    apartamento: Optional[int] = Field(default=None, ge=1, description="Apartamento.")
    apartamento_novo: Optional[int] = Field(
        default=None, ge=1, description="Apartamento novo."
    )
    cep: Optional[str] = Field(default=None, description="CEP.")
    cep_novo: Optional[str] = Field(default=None, description="CEP novo.")
    endereco: Optional[str] = Field(default=None, description="Endereço.")
    endereco_novo: Optional[str] = Field(default=None, description="Endereço novo.")
    numero: Optional[int] = Field(default=None, ge=1, description="Número.")
    numero_novo: Optional[int] = Field(default=None, ge=1, description="Número novo.")
    bairro: Optional[str] = Field(default=None, description="Bairro.")
    bairro_novo: Optional[str] = Field(default=None, description="Bairro novo.")
    cidade: Optional[str] = Field(default=None, description="Cidade.")
    cidade_novo: Optional[str] = Field(default=None, description="Cidade novo.")
    referencia: Optional[str] = Field(default=None, description="Referência.")
    referencia_novo: Optional[str] = Field(default=None, description="Referência nova.")
    complemento: Optional[str] = Field(default=None, description="Complemento.")
    complemento_novo: Optional[str] = Field(
        default=None, description="Complemento novo."
    )
    latitude: Optional[float] = Field(default=None, description="Latitude.")
    latitude_novo: Optional[float] = Field(default=None, description="Latitude nova.")
    longitude: Optional[float] = Field(default=None, description="Longitude.")
    longitude_novo: Optional[float] = Field(default=None, description="Longitude nova.")
    obs: Optional[str] = Field(default=None, description="Observações.")


class LoginOut(BaseModel):
    mensagem: str = Field(description="Mensagem de sucesso.")
