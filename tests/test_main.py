from fastapi import status


def test_index(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "Bem-vindo(a). Para documentação, acesse: https://reddator.newnet.com.br/docs."