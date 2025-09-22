from fastapi import FastAPI
from .api import suporte_router, comercial_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="API do Bot",
    description="Atua como um aggregator, simplificando integrações entre a API aberta do OpaSuite e a API aberta do IXCSoft.",
    version="0.47.0",
)

app.include_router(
    router=suporte_router,
    prefix="/api/v1/suporte",
    tags=["Suporte"],
)
app.include_router(
    router=comercial_router,
    prefix="/api/v1/comercial",
    tags=["Comercial"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://reddator.newnet.com.br/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    path="/",
    summary="Rota padrão, mostra mensagens de boas vindas e URL para acessar esta página.",
)
def index():
    return (
        "Bem-vindo(a). Para documentação, acesse: https://reddator.newnet.com.br/docs."
    )
