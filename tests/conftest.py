import pytest
from app.main import app
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.clients import IXCClient, OpaClient


ixc_client = IXCClient()
opa_client = OpaClient()

@pytest.fixture(scope="session")
def client():
    with TestClient(
        app=app,
    ) as c:
        yield c

@pytest.fixture(scope="session")
async def ixc_async_client():
    async with AsyncClient(
        headers=ixc_client._get_headers,
        timeout=30.0
    ) as ac:
        yield ac

@pytest.fixture(scope="session")
async def opa_async_client():
    async with AsyncClient(
        headers=opa_client.headers,
        timeout=30.0
    ) as ac:
        yield ac