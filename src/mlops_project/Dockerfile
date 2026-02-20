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

# Expõe as portas usadas pelo tracker e pelo model serving
EXPOSE 5000 8000

# Copia e habilita o entrypoint que escolhe entre "mlflow server" e "mlflow models serve"
COPY src/mlops_project/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["sh", "-c", "echo 'No command supplied; entrypoint will start mlflow server by default' && exec /usr/local/bin/docker-entrypoint.sh"]

