from fastapi import FastAPI
from app.api import api_v1_router
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
    title="API do Bot",
    description="Atua como um aggregator, simplificando integrações entre a API do OpaSuite, a API do IXCSoft e a API do 7AZ.",
    version="0.58.0",
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
    summary="Rota padrão, mostra mensagens de boas vindas e URL para acessar página de documentação.",
    response_description="Mensagem de boas-vindas com link para documentação",
)
def index():
    return {
        "mensagem": "Bem-vindo(a) à API do Bot",
        "docs_url": "https://reddator.newnet.com.br/docs",
        "redoc_url": "https://reddator.newnet.com.br/redoc",
    }
