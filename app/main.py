from app.api import api_v1_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, status
from app.api.v1 import database, models, middlewares


def criar_tabelas():
    try:
        models.log.Base.metadata.create_all(bind=database.engine)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar tabelas: {e}",
        )


criar_tabelas()


app = FastAPI(
    title="API do Bot",
    description="Atua como um aggregator, simplificando integrações entre a API do OpaSuite, a API do IXCSoft e a API do 7AZ.",
    version="0.56.8",
)

app.add_middleware(middlewares.LogsMiddleware)

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
