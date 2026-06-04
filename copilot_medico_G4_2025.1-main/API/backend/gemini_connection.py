import os
from groq import Groq
from . import patient_db

# Configuração da API Groq
try:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente GROQ_API_KEY não foi encontrada.")
    client = Groq(api_key=api_key)
except ValueError as e:
    print(f"Erro de configuração da API Groq: {e}")
    raise

# Carregar Instrução do Sistema (Co-Pilot_medico.txt)
try:
    system_instruction_file = os.path.join(os.path.dirname(__file__), 'Co-Pilot_medico.txt')
    if not os.path.exists(system_instruction_file):
        raise FileNotFoundError(f"Arquivo de instrução do sistema não encontrado em: {system_instruction_file}")
    system_instruction_content = open(system_instruction_file, encoding='utf-8').read()
except FileNotFoundError as e:
    print(f"Erro: {e}")
    raise

# Modelo de alta performance do Groq
MODEL_NAME = "llama-3.3-70b-versatile"

def send_message(patient_id: str, consultation_id: str, message_text: str) -> str:
    """
    Envia o histórico de chat da consulta formatado junto com a nova mensagem para o Groq.
    """
    try:
        # 1. Carregar histórico da consulta específica
        history_from_db = patient_db.get_consultation_chat_history(patient_id, consultation_id)

        # 2. Formatar o histórico no padrão de Chat do Groq (sistema, usuário e assistente)
        messages = [{"role": "system", "content": system_instruction_content}]
        
        if history_from_db:
            for msg in history_from_db:
                # O banco usa 'model', mas o Groq/Llama espera 'assistant'
                role = "assistant" if msg["role"] == "model" else msg["role"]
                text = msg["parts"][0]["text"] if "parts" in msg and len(msg["parts"]) > 0 else ""
                messages.append({"role": role, "content": text})

        # 3. Enviar requisição para a API do Groq
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3,
            max_tokens=4096,
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(f"Erro ao enviar mensagem para a API Groq para paciente {patient_id}, consulta {consultation_id}: {e}")
        return f"Desculpe, ocorreu um erro de comunicação com a IA do Groq: {str(e)}"