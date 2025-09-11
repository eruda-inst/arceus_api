from fastapi import FastAPI, status
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/")
def index():
    return "Bem-vindo(a) à API do Roberto. Para documentação, acesse: http://127.0.0.1:8000/docs."

client = TestClient(app)

def test_index():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "Bem-vindo(a) à API do Roberto. Para documentação, acesse: http://127.0.0.1:8000/docs."