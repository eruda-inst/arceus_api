from api_roberto.app.utils.helpers.rotular import rotular_status_conexao, rotular_status_contrato, rotular_status_atendimento


def test_rotular_status_conexao():
    assert rotular_status_conexao("S") == "Conectado"
    assert rotular_status_conexao("SS") == "Sem status"
    assert rotular_status_conexao("N") == "Desconectado"


def test_rotular_status_contrato():
    assert rotular_status_contrato("P") == "Pré-contrato"
    assert rotular_status_contrato("A") == "Ativo"
    assert rotular_status_contrato("I") == "Inativo"
    assert rotular_status_contrato("N") == "Negativado"
    assert rotular_status_contrato("D") == "Desistiu"


def test_rotular_status_atendimento():
    assert rotular_status_atendimento("N") == "Novo"
    assert rotular_status_atendimento("P") == "Pendente"
    assert rotular_status_atendimento("EP") == "Em progresso"
    assert rotular_status_atendimento("S") == "Solucionado"
    assert rotular_status_atendimento("C") == "Cancelado"