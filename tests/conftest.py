import pytest
from app.main import app
from httpx import AsyncClient
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    with TestClient(app=app) as c:
        yield c

@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient() as ac:
        yield ac
