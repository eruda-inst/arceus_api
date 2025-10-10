from typing import Dict
from app.api import api_v1_router
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from app.api.v1 import middlewares, database
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.criar_tabelas()
    print("Tabelas criadas com sucesso!")
    yield
    print("Encerrando aplicação...")


app = FastAPI(
    title="Aggregator",
    description="""
    API oficial Newnet/Eruda - Simplifica integrações entre a API (Application Programming Interface) da OpaSuite, da IXCSoft e da 7AZ.
    """,
    version="0.58.4",
    lifespan=lifespan,
)

app.add_middleware(middlewares.LogMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://reddator.newnet.com.br"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=api_v1_router, prefix="/api/v1")


@app.get(
    path="/",
    summary="Rota padrão, mostra mensagem de boas-vindas e URL para acessar página de documentação.",
)
def index(request: Request) -> Dict:
    base_url = str(request.base_url).rstrip("/")

    return {
        "mensagem": "Bem-vindo(a) ao Aggregator.",
        "docs_url": f"{base_url}{app.docs_url}",
        "redoc_url": f"{base_url}{app.redoc_url}",
    }
