# Usa uma imagem base de Python compatível com pacotes modernos e MLflow
# FROM python:3.11-slim
FROM python:3.12-slim

# Instala dependências do sistema necessárias para MLflow e outros pacotes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* 
RUN pip install mlflow psycopg2-binary boto3 

# Define o diretório de trabalho dentro do container para /app
WORKDIR /app

# Copia os ficheiros de dependências e instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante código do projeto para o diretório de trabalho no container (/app)
COPY . . 

# Expõe a porta do MLflow para permitir acesso externo (ajuste conforme necessário)
EXPOSE 5000 

# Comando para iniciar o servidor do MLflow (ajuste conforme necessário)
# 'mlflow server' já serve a interface web; o argumento 'ui' não é suportado nas versões
# mais recentes e provoca o erro "unexpected extra argument (ui)".
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000"]

