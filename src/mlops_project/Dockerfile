# Usa uma imagem base de Python
FROM python:3.9-slim

# Instala dependências
RUN pip install mlflow==2.0.0 psycopg2-binary boto3

# Define o diretório de trabalho
WORKDIR /app

# Copia os ficheiros de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante código do projeto
COPY . .

# Expõe a porta do MLflow
EXPOSE 5000

# Comando para iniciar o servidor do MLflow (ajuste conforme necessário)
CMD ["mlflow", "server", "ui", "--host", "0.0.0.0", "--port", "5000"]

