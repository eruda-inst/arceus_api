from fastapi import FastAPI
from .api import suporte_router


app = FastAPI(
    title="API do Bot",
    description="Atua como um aggregator, simplificando integrações entre a API aberta do OpaSuite e a API aberta do IXCSoft.",
    version="0.45.3",
)

app.include_router(router=suporte_router, prefix="/api/v1/suporte", tags=["Suporte"])

@app.get("/", summary="Rota padrão, mostra mensagens de boas vindas e URL para acessar esta página.")
def index():
    return "Bem-vindo(a). Para documentação, acesse: https://reddator.newnet.com.br/docs."