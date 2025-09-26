from .api import api_v1
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="API do Bot",
    description="Atua como um aggregator, simplificando integrações entre a API aberta do OpaSuite e a API aberta do IXCSoft.",
    version="0.50.9",
)

app.include_router(router=api_v1, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://reddator.newnet.com.br/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    path="/",
    summary="Rota padrão, mostra mensagens de boas vindas e URL para acessar página de documentação.",
)
def index():
    return (
        "Bem-vindo(a). Para documentação, acesse: https://reddator.newnet.com.br/docs."
    )
