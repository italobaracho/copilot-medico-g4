# Usar imagem oficial do Python 3.11-slim
FROM python:3.11-slim

# Definir diretório de trabalho no container
WORKDIR /app

# Instalar dependências de compilação básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Baixar o modelo pt_core_news_lg do spaCy
RUN python -m spacy download pt_core_news_lg

# Copiar o restante dos arquivos do backend
COPY copilot_medico_G4_2025.1-main/API /app/

# Expor a porta que a API utiliza
EXPOSE 3001

# Definir a variável de ambiente
ENV PYTHONUNBUFFERED=1

# Comando para rodar a aplicação
CMD ["python", "server.py"]
