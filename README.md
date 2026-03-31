# API do Bot

## Visão Geral

A API do Bot atua como um serviço agregador, simplificando a integração entre a API do OpaSuite, a API do IXCSoft e a API do 7AZ. Desenvolvida em FastAPI, oferece endpoints unificados para gerenciamento de clientes, contratos, atendimentos, status de conexão e operações financeiras.

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

- **Python 3.12+**
- **FastAPI**
- **Pydantic** / **Pydantic Settings**
- **HTTPX**
- **SQLAlchemy**
- **Alembic**
- **psycopg / asyncpg**
- **Docker**
- **uv**

## Configuração do Ambiente

### Pré-requisitos

- Python 3.12+
- Docker (opcional, para execução em container)

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
OPA_TOKEN=seu_token_opa
IXC_TOKEN=seu_token_ixc
OPA_HOST=seu_host_opa
IXC_HOST=seu_host_ixc
API_KEY_7AZ=sua_api_key_7az
BASE_URL_7AZ=sua_base_url_7az
DB_URL=postgresql://usuario:senha@localhost:5432/seu_banco
MIGRATE_DB_URL=postgresql://usuario:senha@localhost:5432/seu_banco
```

> Se você estiver usando Docker Compose localmente, `DB_URL` deve apontar para o container de banco de dados ou estar configurado via `MIGRATE_DB_URL`.

### Instalação

1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd arceus
   ```
2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install uv
   uv sync --no-cache
   ```

### Executando a Aplicação

Para executar a aplicação em modo de desenvolvimento com hot-reload:

```bash
python -m uvicorn app.main:app --reload
```

Alternativamente, utilize Docker Compose com o arquivo `compose.yml`:

```bash
docker compose -f compose.yml up -d
```

Após iniciar, a documentação interativa da API estará disponível em [http://localhost:8000/docs](http://localhost:8000/docs).

## Migrações (Alembic)

Este projeto usa Alembic para versionamento do schema do banco de dados. Dependendo de como o banco está rodando (dentro de containers Docker ou localmente), existem duas formas comuns de aplicar as migrações:

1. Executar Alembic dentro do ambiente Docker (recomendado quando o banco está no Docker)

- Primeiro suba o serviço de banco de dados:

```bash
docker compose -f compose.yml up -d db
```

- Em seguida, execute Alembic no container da aplicação:

```bash
docker compose -f compose.yml run --rm api alembic upgrade head
```

ou, se a aplicação já estiver rodando:

```bash
docker compose -f compose.yml exec api alembic upgrade head
```

2. Executar Alembic localmente contra um banco acessível (por exemplo, Postgres em localhost)

- Use `MIGRATE_DB_URL` para evitar problemas de resolução de host quando o `DB_URL` estiver apontando para um container Docker:

```bash
MIGRATE_DB_URL="postgresql://larissa_user:segurademais@localhost:5432/larissa_db" alembic upgrade head
```

- Quando presente, o projeto deve usar `MIGRATE_DB_URL` em vez do `DB_URL` carregado do `.env`.

3. Alternativa (menos ideal): editar temporariamente o `.env` para apontar `DB_URL` para um host resolvível pelo seu ambiente local (por exemplo, `localhost`).

> Observação: se o banco estiver em Docker e você executar Alembic localmente sem ajuste, o host `db` no `DB_URL` não será resolvido pelo seu sistema host.

## Estrutura do Projeto

```
.
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── clients/
│   │       ├── cores/
│   │       ├── cruds/
│   │       ├── db/
│   │       ├── middlewares/
│   │       ├── models/
│   │       ├── routers/
│   │       ├── schemas/
│   │       ├── services/
│   │       └── utils/
│   └── main.py
├── alembic.ini
├── alembic/
├── compose.yml
├── Dockerfile
├── pyproject.toml
├── uv.lock
├── README.md
└── wait-for-it.sh
```
