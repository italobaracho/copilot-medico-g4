import os
import json
from unittest.mock import patch

# Define a chave de API fictícia antes de qualquer importação para evitar que o import de gemini_connection falhe
os.environ["GROQ_API_KEY"] = "dummy_key_for_unit_tests"

import pytest
from server import app
from backend import patient_db

@pytest.fixture
def client(tmp_path):
    # Sobrescreve o DB_FILE no patient_db
    original_db = patient_db.DB_FILE
    temp_db_file = str(tmp_path / "patients_db_server_test.json")
    patient_db.DB_FILE = temp_db_file
    
    # Inicializa banco de dados vazio
    patient_db.save_database({})
    
    # Cria o cliente de testes do Flask
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
        
    # Restaura o DB_FILE original
    patient_db.DB_FILE = original_db
    if os.path.exists(temp_db_file):
        try:
            os.remove(temp_db_file)
        except Exception:
            pass

def test_check_patient_exists(client):
    # Paciente não existe
    response = client.get('/api/patient-exists/non-existent-id')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["exists"] is False

    # Cria e verifica se existe
    patient_db.ensure_patient_exists("exists-123", name="Paciente Existe")
    response = client.get('/api/patient-exists/exists-123')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["exists"] is True

def test_create_patient(client):
    response = client.post('/api/patients', json={"name": "Maria Sousa"})
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["status"] == "success"
    assert "patient_id" in data
    assert data["patient_name"] == "Maria Sousa"
    assert "first_consultation_id" in data

@patch('backend.gemini_connection.send_message')
def test_chat_message(mock_send_message, client):
    mock_send_message.return_value = "Olá, eu sou o Gemini Mockado!"
    
    # Cria paciente e consulta
    p_id = "p-123"
    patient_db.ensure_patient_exists(p_id, name="João")
    c_id = patient_db.add_consultation_to_patient(p_id, "Consulta Principal")
    
    response = client.post('/api/chat', json={
        "message": "Qual é a dosagem do paracetamol?",
        "patient_id": p_id,
        "consultation_id": c_id
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "success"
    assert data["ai_response"] == "Olá, eu sou o Gemini Mockado!"
    assert data["consultation_id"] == c_id
    
    # Verifica se chamou o Gemini com o texto filtrado (remover_nomes remove nomes se houver, mas aqui não há nomes de pessoas)
    mock_send_message.assert_called_once_with(p_id, c_id, "Qual é a dosagem do paracetamol?")

@patch('backend.gemini_connection.send_message')
def test_extracted_data_popup_format(mock_send_message, client):
    mock_send_message.return_value = "Recebi e analisei os dados do prontuário."
    
    p_id = "p-123"
    patient_db.ensure_patient_exists(p_id, name="Lucas")
    c_id = patient_db.add_consultation_to_patient(p_id, "Consulta 1")
    
    # Formato do popup (App.tsx)
    payload = {
        "patient_id": p_id,
        "consultation_id": c_id,
        "extracted_data": {
            "editableNotes": "Paciente queixa-se de dor lombar crônica.",
            "createInputs": ["Pressão: 120/80", "Peso: 75kg"]
        }
    }
    
    response = client.post('/api/extracted-data', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "success"
    assert data["ai_response"] == "Recebi e analisei os dados do prontuário."

@patch('backend.gemini_connection.send_message')
def test_extracted_data_floating_button_format(mock_send_message, client):
    mock_send_message.return_value = "Dados recebidos pelo botão flutuante analisados."
    
    p_id = "p-123"
    patient_db.ensure_patient_exists(p_id, name="Lucas")
    c_id = patient_db.add_consultation_to_patient(p_id, "Consulta 1")
    
    # Formato do botão flutuante (background.js)
    payload = {
        "patient_id": p_id,
        "consultation_id": c_id,
        "extracted_content": [
            {"role": "peso", "text": "80kg"},
            {"role": "altura", "text": "1.75m"},
            "Paciente com febre leve"
        ]
    }
    
    response = client.post('/api/extracted-data', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "success"
    assert data["ai_response"] == "Dados recebidos pelo botão flutuante analisados."
