"""
Application entry point for the Arceus API.

Configures FastAPI, registers routers, middleware, CORS, and manages
lifespan events (startup/shutdown).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import HttpUrl

from .api import api_v1_router
from .api.v1 import clients, middlewares, schemas


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan events.

    On startup, no specific initialization is required.
    On shutdown, gracefully close all HTTP clients used by the application.

    Args:
        app: The FastAPI application instance.
    """
    # Startup logic (runs before the app starts receiving requests)
    # You can add any initialization code here if needed.
    yield
    # Shutdown logic (runs when the app is shutting down)
    await clients.IxcAcsClient.aclose()
    await clients.OpaClient.aclose()
    await clients.SevenAZClient.aclose()
    await clients.IxcClient.aclose()


app = FastAPI(
    title="Arceus",
    description="Integra com sistemas IXC, IXC ACS, Opa e 7AZ. Oferece autenticação, gestão de usuários e permissões, operações comerciais (contratos, leads), financeiras (faturas, cobrança), suporte (atendimentos, status de conexão), além de logs e métricas para monitoramento",
    version="1.10.0",
    lifespan=lifespan,
)

# Enable CORS for all origins
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the aggregated API v1 router, including all HTTP and WebSocket endpoints
app.include_router(router=api_v1_router)

# Custom middleware to log requests/responses for specified endpoints
app.add_middleware(middlewares.LogMiddleware)


@app.get(path="/", summary="Endpoint raíz da API")
def root(request: Request) -> schemas.RootOutSchema:
    """
    Return general information about the API.

    Args:
        request: The incoming HTTP request.

    Returns:
        RootOutSchema containing the API title, description, and documentation URLs.
    """
    title = app.title
    description = app.description
    base_url = str(request.base_url).rstrip("/")
    docs_url = HttpUrl(base_url + str(app.docs_url))
    redoc_url = HttpUrl(base_url + str(app.redoc_url))
    return schemas.RootOutSchema(
        titulo=title, descricao=description, url_docs=docs_url, url_redoc=redoc_url
    )
