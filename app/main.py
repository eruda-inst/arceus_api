from fastapi import FastAPI
from .routers import router as aggregator_router


app = FastAPI(
    title="API do Bot",
    description="Atua como um aggregator, simplificando integrações entre a API aberta do OpaSuite e a API aberta do IXCSoft.",
    version="0.41.2"
)

app.include_router(router=aggregator_router, prefix="/api/v1", tags=["Aggregator"])

@app.get("/")
def index():
    return "Bem-vindo(a). Para documentação, acesse: https://reddator.newnet.com.br/docs."