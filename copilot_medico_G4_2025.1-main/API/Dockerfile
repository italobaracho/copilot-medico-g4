# Usar imagem oficial do Python 3.11-slim
FROM python:3.11-slim

# Definir diretório de trabalho no container
WORKDIR /app

# Instalar dependências de compilação básicas se necessário (spacy usa C++ extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt da raiz para o container
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Baixar o modelo pt_core_news_lg do spaCy (requerido para filtragem de nomes)
RUN python -m spacy download pt_core_news_lg

# Copiar o restante dos arquivos do backend
COPY copilot_medico_G4_2025.1-main/API /app/

# Expor a porta que a API utiliza
EXPOSE 3001

# Definir a variável de ambiente para garantir que os prints do python apareçam no console do docker
ENV PYTHONUNBUFFERED=1

# Comando para rodar a aplicação
CMD ["python", "server.py"]
