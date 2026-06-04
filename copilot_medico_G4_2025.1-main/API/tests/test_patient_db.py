import os
import pytest
from backend import patient_db

@pytest.fixture(autouse=True)
def setup_temp_db(tmp_path):
    # Salva o caminho do arquivo de banco de dados original
    original_db = patient_db.DB_FILE
    # Define o novo arquivo de testes temporário
    temp_db_file = str(tmp_path / "patients_db_test.json")
    patient_db.DB_FILE = temp_db_file
    
    # Cria um banco de dados vazio para o início do teste
    patient_db.save_database({})
    
    yield
    
    # Restaura o caminho do banco de dados original
    patient_db.DB_FILE = original_db
    if os.path.exists(temp_db_file):
        try:
            os.remove(temp_db_file)
        except Exception:
            pass

def test_ensure_patient_exists():
    p_id = "test-patient-123"
    # Cria o paciente
    data = patient_db.ensure_patient_exists(p_id, name="Test Patient")
    assert data["name"] == "Test Patient"
    assert data["chat_history"] == []
    assert data["consultations"] == []
    
    # Verifica se salvou e carregou corretamente
    loaded = patient_db.get_patient_data(p_id)
    assert loaded["name"] == "Test Patient"

def test_add_consultation_to_patient():
    p_id = "test-patient-123"
    patient_db.ensure_patient_exists(p_id, name="Test Patient")
    
    # Adiciona consulta
    c_id = patient_db.add_consultation_to_patient(p_id, "Consulta de Rotina")
    assert c_id is not None
    
    # Verifica consultas do paciente
    consultations = patient_db.get_patient_consultations(p_id)
    assert len(consultations) == 1
    assert consultations[0]["id"] == c_id
    assert consultations[0]["title"] == "Consulta de Rotina"

def test_add_message_to_consultation_history():
    p_id = "test-patient-123"
    patient_db.ensure_patient_exists(p_id, name="Test Patient")
    c_id = patient_db.add_consultation_to_patient(p_id, "Consulta de Rotina")
    
    # Adiciona mensagens ao histórico da consulta
    patient_db.add_message_to_consultation_history(p_id, c_id, "user", "Dor nas costas")
    patient_db.add_message_to_consultation_history(p_id, c_id, "model", "Entendido, qual o local exato?")
    
    # Verifica o histórico da consulta
    history = patient_db.get_consultation_chat_history(p_id, c_id)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["parts"][0]["text"] == "Dor nas costas"
    assert history[1]["role"] == "model"
    assert history[1]["parts"][0]["text"] == "Entendido, qual o local exato?"
