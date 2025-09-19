# API da Larissa

## Visão Geral

A API do Roberto é um serviço agregador que simplifica a integração entre a API do OpaSuite e a API do IXCSoft. Desenvolvida em FastAPI, oferece endpoints unificados para gerenciamento de clientes, contratos, atendimentos, status de conexão, dentre outros.

## Funcionalidades Principais

- ✅ Consulta de contratos ativos de clientes
- ✅ Verificação de status de conexão
- ✅ Consulta de status de contratos
- ✅ Monitoramento de status de ONUs
- ✅ Abertura de tickets de atendimento
- ✅ Envio de sinais de desconexão
- ✅ Verificação de atendimentos em aberto

## Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **Pydantic** - Validação de dados e configurações
- **HTTPX** - Cliente HTTP assíncrono
- **Pytest** - Framework de testes
- **Python 3.8+** - Linguagem de programação

## Configuração do Ambiente

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
OPA_TOKEN=seu_token_opa
IXC_TOKEN=seu_token_ixc
```

### Instalação de Dependências

```bash
pip install -r requirements.txt
```

### Executando a Aplicação

```bash
uvicorn app.main:app --reload
```

Ou

```bash
docker compose up -d
```

A documentação interativa da API estará disponível em: https://reddator.newnet.com.br/docs

## Estrutura do Projeto

```
app/
├── clients/           # Clientes para APIs externas
│   ├── ixc.py         # Cliente para integração com IXCSoft
│   └── opa.py         # Cliente para integração com OpaSuite
├── core/              # Configurações principais
│   └── config.py      # Configurações da aplicação (variáveis de ambiente)
├── routers/           # Definição de rotas da API
│   └── aggregator.py  # Rotas principais do aggregator
├── schemas/           # Modelos Pydantic (schemas)
│   ├── atendimento.py # Schemas para atendimentos
│   ├── conexao.py     # Schemas para status de conexão
│   ├── contrato.py    # Schemas para contratos
│   ├── misc.py        # Schemas auxiliares (Meta, Links)
│   └── onu.py         # Schemas para status de ONU
├── services/          # Lógica de negócio e serviços
│   └── aggregator.py  # Serviço principal do aggregator
├── utils/             # Utilitários e helpers
│   └── helpers/
│       └── rotular.py # Funções para rotular status
├── main.py            # Aplicação FastAPI principal
└── __init__.py        # Arquivos de inicialização do pacote

tests/                 # Testes automatizados
├── conftest.py        # Configurações do pytest
├── test_main.py       # Testes do endpoint principal
└── test_rotular.py    # Testes das funções de rotulagem

docker-compose.yaml    # Configuração do Docker Compose
Dockerfile             # Instruções de build da imagem Docker
pytest.ini             # Configuração do Pytest
requirements.txt       # Dependências do projeto
README.md              # Documentação do projeto
```

## Exemplos de Uso

### Consultar Contratos Ativos

```bash
GET /api/v1/contratos_ativos_cliente?protocolo_atendimento_opa=123456789012
```

### Verificar Status de Conexão

```bash
GET /api/v1/status_conexao?id_login_ixc=12345
```

### Abrir Atendimento

```bash
POST /api/v1/abrir_atendimento
{
  "id_login": 12345,
  "id_assunto": 1,
  "id_cliente": 67890,
  "menssagem": "Problema de conexão",
  "titulo": "Cliente sem internet",
  "id_ticket_setor": 1,
  "id_contrato": 54321
}
```

## Testes

Execute a suíte de testes:

```bash
python -m pytest
```
