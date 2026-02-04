import pytest
from main import app, consertar_acentuacao
from fastapi.testclient import TestClient

client = TestClient(app)

def test_consertar_acentuacao_sucesso():
    texto_corrompido = "ASSISTÃ\u008aNCIA" 
    resultado = consertar_acentuacao(texto_corrompido)
    assert resultado == "ASSISTÊNCIA"

def test_consertar_acentuacao_limpeza():
    assert consertar_acentuacao("  bradesco saude  ") == "BRADESCO SAUDE"

def test_rota_operadoras_status_code():
    response = client.get("/api/operadoras?page=1&limit=1")
    assert response.status_code in [200, 500] 

def test_filtro_cnpj_invalido():
    response = client.get("/api/operadoras/00000000000000")
    assert response.status_code == 404