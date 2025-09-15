from fastapi import status


def test_index(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "Bem-vindo(a) à API do Roberto. Para documentação, acesse: http://127.0.0.1:8000/docs."