from pydantic import HttpUrl
from .api import api_v1_router
from fastapi import FastAPI, Request
from .api.v1 import schemas, middlewares
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Arceus",
    description="Simplifica integrações entre a API da OpaSuite, IXCSoft e 7AZ.",
    version="1.0.0",
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
    Retorna informações sobre a API, incluíndo URLs para documentações docs e redoc.
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
