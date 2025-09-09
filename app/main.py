from fastapi import FastAPI
from app.api.v1.routes.aggregator import router as aggregator_router


app = FastAPI(
    title="API do Roberto",
    description="Atua como um aggregator, simplificando integrações entre a API aberta do OpaSuite e a API aberta do IXCSoft.",
    version="0.33.4"
)


app.include_router(router=aggregator_router, prefix="/api/v1", tags=["aggregator"])


@app.get("/")
def index():
    return {"message": "Bem-vindo(a) à API do Roberto. Para documentação, abra: http://127.0.0.1:8000/docs."}