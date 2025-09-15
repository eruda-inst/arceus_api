from fastapi import FastAPI
from .routes import router as aggregator_router


app = FastAPI(
    title="API do Roberto",
    description="Atua como um aggregator, simplificando integrações entre a API aberta do OpaSuite e a API aberta do IXCSoft.",
    version="0.39.8"
)

app.include_router(router=aggregator_router, prefix="/api/v1", tags=["aggregator"])

@app.get("/")
def index():
    return "Bem-vindo(a) à API do Roberto. Para documentação, acesse: http://127.0.0.1:8000/docs."