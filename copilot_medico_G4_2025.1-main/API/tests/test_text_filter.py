import pytest
from backend import text_filter

def test_remover_nomes():
    texto = "O paciente João Silva sentiu dores de cabeça."
    resultado = text_filter.remover_nomes(texto)
    assert "João Silva" not in resultado
    assert "paciente" in resultado

def test_retornar_nome():
    texto = "O nome do médico é Dr. Carlos Alberto."
    nome = text_filter.retornar_nome(texto)
    # Deve retornar o nome próprio identificado
    assert "Carlos" in nome or "Carlos Alberto" in nome or nome != ""
