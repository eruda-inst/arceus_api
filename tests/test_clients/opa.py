import pytest
from unittest.mock import AsyncMock, patch
from app.clients import OpaClient

@pytest.mark.asyncio
@patch('app.clients.OpaClient.get_id_cliente_opa', new_callable=AsyncMock)
async def test_get_id_cliente_opa(mock_get_id_cliente):
    protocolo_atendimento_opa = "NWT202537196"
    expected_response = {
        'status': 'success',
        'code': 200,
        'data': [{...}]
    }
    
    mock_get_id_cliente.return_value = expected_response
    
    client = OpaClient()
    res = await client.get_id_cliente_opa(protocolo_atendimento_opa)
    
    assert res == expected_response
    mock_get_id_cliente.assert_awaited_once_with(protocolo_atendimento_opa)