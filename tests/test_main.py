from ..app.main import app
from fastapi import status
from fastapi.testclient import TestClient


client = TestClient(app)


def test_index():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "Bem-vindo(a) à API do Roberto. Para documentação, acesse: http://127.0.0.1:8000/docs."