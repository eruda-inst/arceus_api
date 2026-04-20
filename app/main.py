from .api import api_v1_router
from pydantic import AnyHttpUrl
from fastapi import FastAPI, Request
from .api.v1 import schemas, middlewares
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="API do Arceus",
    description="API oficial Newnet/Eruda - Simplifica integrações entre a API da OpaSuite, da IXCSoft e da 7AZ.",
    version="0.77.4",
    routes=api_v1_router.routes,
)


app.add_middleware(middlewares.LogMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    path="/",
    response_model=schemas.RootOut,
    summary="Endpoint Raiz da API.",
    description="Retorna os links para a documentação interativa da API.",
)
def root(request: Request) -> schemas.RootOut:
    base_url = str(request.base_url).rstrip("/")
    docs_url = AnyHttpUrl(base_url + str(app.docs_url))
    redoc_url = AnyHttpUrl(base_url + str(app.redoc_url))
    return schemas.RootOut(docs_url=docs_url, redoc_url=redoc_url)
