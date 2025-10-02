# API do Bot

## Visão Geral

A API do Bot atua como um serviço agregador, simplificando a integração entre a API do OpaSuite, a API do IXCSoft e a API do 7AZ. Desenvolvida em FastAPI, oferece endpoints unificados para gerenciamento de clientes, contratos, atendimentos, status de conexão, entre outros.

## Funcionalidades Principais

### Comercial
- ✅ Consulta de status de acesso
- ✅ Consulta de contratos
- ✅ Cadastro de leads

### Financeiro
- ✅ Consulta de faturas em aberto
- ✅ Consulta de contratos
- ✅ Desbloqueio em confiança
- ✅ Obtenção de linha digitável de faturas
- ✅ Obtenção de chave PIX de faturas

### Suporte
- ✅ Consulta de contratos ativos
- ✅ Verificação de status de conexão
- ✅ Monitoramento de status de ONUs
- ✅ Abertura de tickets de atendimento
- ✅ Envio de sinais de desconexão
- ✅ Verificação de atendimentos em aberto
- ✅ Atualização de informações de login
- ✅ Limpeza de MAC address

### Triagem
- ✅ Atualização de informações de clientes

## Tecnologias Utilizadas

- **Python 3.8+**
- **FastAPI** - Framework web moderno e rápido para construção de APIs.
- **Pydantic** - Validação de dados e gerenciamento de configurações.
- **HTTPX** - Cliente HTTP assíncrono para realizar requisições a outras APIs.
- **Docker** - Plataforma de containerização para fácil deploy e escalabilidade.

## Configuração do Ambiente

### Pré-requisitos

- Python 3.8+
- Docker (opcional, para execução em container)

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto, baseado no `.env_example`, com as seguintes variáveis:

```env
OPA_TOKEN=seu_token_opa
IXC_TOKEN=seu_token_ixc
OPA_HOST=seu_host_opa
IXC_HOST=seu_host_ixc
API_KEY_7AZ=sua_api_key_7az
BASE_URL_7AZ=sua_base_url_7az
```

### Instalação

1.  Clone o repositório:
    ```bash
    git clone <url-do-repositorio>
    cd backend-larissa
    ```
2.  Crie e ative um ambiente virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

### Executando a Aplicação

Para executar a aplicação em modo de desenvolvimento com hot-reload:

```bash
uvicorn app.main:app --reload
```

Alternativamente, utilize Docker Compose para subir a aplicação:

```bash
docker compose up -d
```

Após iniciar, a documentação interativa da API (Swagger UI) estará disponível em [http://localhost:8000/docs](http://localhost:8000/docs).

## Estrutura do Projeto

```
.
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── clients/
│   │       ├── core/
│   │       ├── routers/
│   │       │   ├── comercial.py
│   │       │   ├── financeiro.py
│   │       │   ├── suporte.py
│   │       │   └── triagem.py
│   │       ├── schemas/
│   │       ├── services/
│   │       └── utils/
│   ├── main.py
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```