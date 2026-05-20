from pydantic import HttpUrl
from .api import api_v1_router
from fastapi import FastAPI, Request
from .api.v1 import schemas, middlewares
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API do Arceus",
    description="API oficial Newnet/Eruda — Simplifica integrações entre a API da OpaSuite, da IXCSoft e da 7AZ.",
    version="Mark I (0.89.1)",
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


@app.get(path="/", summary="Endpoint Raiz da API.")
def index(request: Request) -> schemas.IndexOut:
    """
    Retorna os links para a documentação interativa da API.
    """
    titulo = app.title
    descricao = app.description
    base_url = str(request.base_url).rstrip("/")
    url_documentacao_docs = HttpUrl(base_url + str(app.docs_url))
    url_documentacao_redoc = HttpUrl(base_url + str(app.redoc_url))
    return schemas.IndexOut(
        titulo=titulo,
        descricao=descricao,
        url_documentacao_docs=url_documentacao_docs,
        url_documentacao_redoc=url_documentacao_redoc,
    )
