from typing import Dict
from app.api import api_v1_router
from app.api.v1 import middlewares
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Aggregator",
    description="""
    API oficial Newnet/Eruda - Simplifica integrações entre a API (Application Programming Interface) da OpaSuite, da IXCSoft e da 7AZ.
    """,
    version="0.66.1",
    routes=api_v1_router.routes,
    middlewar=middlewares.LogMiddleware,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    path="/",
    summary="Rota padrão, mostra mensagem de boas-vindas e URL para acessar página de documentação.",
)
def index(request: Request) -> Dict:
    """
    Endpoint da raiz que fornece URLs para a documentação da API.

    Args:
        request (Request): O objeto da requisição FastAPI.

    Returns:
        Dict: Um dicionário contendo uma mensagem de boas-vindas
              e as URLs para a documentação (Swagger e Redoc).
    """
    base_url = str(request.base_url).rstrip("/")

    return {
        "mensagem": "Bem-vindo(a) ao Aggregator.",
        "docs_url": f"{base_url}{app.docs_url}",
        "redoc_url": f"{base_url}{app.redoc_url}",
    }
