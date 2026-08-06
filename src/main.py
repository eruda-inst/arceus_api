from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import HttpUrl

from .api.v1 import api_v1_router, middlewares, schemas

app = FastAPI(
    title="Arceus",
    description="Integra com sistemas IXC, Opa e 7AZ. Oferece autenticação, gestão de usuários e permissões, operações comerciais (contratos, leads), financeiras (faturas, cobrança), suporte (atendimentos, status de conexão), além de logs e métricas para monitoramento",
    version="1.0",
    routes=api_v1_router.routes,
)


app.add_middleware(middlewares.LogMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(path="/", summary="Endpoint raíz da API")
def index(request: Request) -> schemas.IndexOut:
    """
    Retorna informações sobre a API.
    """
    titulo = app.title
    descricao = app.description
    base_url = str(request.base_url).rstrip("/")
    docs_url = HttpUrl(base_url + str(app.docs_url))
    redoc_url = HttpUrl(base_url + str(app.redoc_url))
    return schemas.IndexOut(
        titulo=titulo,
        descricao=descricao,
        docs_url=docs_url,
        redoc_url=redoc_url,
    )
