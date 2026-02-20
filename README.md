# 🚀 End-to-End MLflow Project

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![MLflow](https://img.shields.io/badge/MLOps-MLflow-orange?logo=mlflow)
![GitHub Actions](https://img.shields.io/badge/CI/CD-GitHub%20Actions-lightgrey?logo=githubactions&logoColor=blue)
![Lint](https://img.shields.io/badge/Lint-Flake8-yellow?logo=python)
![Tests](https://img.shields.io/badge/Tests-Pytest-green?logo=pytest)
![License](https://img.shields.io/badge/License-MIT-success?logo=open-source-initiative)

---

## 📖 Visão Geral (PT-BR)
Este projeto demonstra a construção de um pipeline **end-to-end de Machine Learning** com **MLflow**, cobrindo todas as etapas de **MLOps**:  
- Ingestão e pré-processamento de dados  
- Treinamento e rastreamento de experimentos  
- Avaliação e seleção de modelos  
- Deployment em ambiente produtivo  

O objetivo é servir como um **cartão de visitas técnico**, mostrando experiência prática em **engenharia de machine learning aplicada a produção**.

---

## 📖 Overview (EN)
This project demonstrates the implementation of an **end-to-end Machine Learning pipeline** using **MLflow**, covering all **MLOps** stages:  
- Data ingestion and preprocessing  
- Model training and experiment tracking  
- Model evaluation and selection  
- Deployment into production environment  

The goal is to serve as a **technical portfolio project**, showcasing practical experience in **machine learning engineering applied to production**.

---

## 🏗️ Arquitetura / Architecture
Estrutura de pastas do projeto após reorganização:

```
end-to-end-mlflow-project/
│── docs/                  # documentação, guias e cheatsheets
│   │── fastapi/           # API-related docs (endpoints, cheatsheet, summary)
│   │── monitoring/        # Prometheus/Grafana material, quick-start
│   │── usage/             # passo a passo / instructions
│   │── MLFLOW_SOLUTION.md # arquitetura geral e notas
│── notebooks/             # Jupyter notebooks e experiment notes
│── src/                   # código-fonte do pacote Python
│   └── mlops_project/
│       ├── api.py
│       ├── train.py
│       ├── evaluate.py
│       ├── deploy.py
│       ├── utils.py
│       └── ...            # demais módulos
│── tests/                 # suite de testes pytest
│── k8s/                   # manifests de Kubernetes
│── scripts/               # utilitários de shell
│── requirements.txt       # lista de dependências (pip)
│── pyproject.toml         # configurações de empacotamento
│── README.md              # documentação principal
│── .gitignore             # arquivos ignorados pelo Git
```

A convenção `src/` garante que o pacote `mlops_project` seja instalado via `pip install -e .` e evita problemas com importação relativa em testes.

---

## ⚙️ Tecnologias / Technologies
- **Python 3.9+**  
- **MLflow** (Tracking, Models, UI)  
- **Git + GitHub** for version control  
- Modular structure following engineering best practices  

---

## 🔬 MLflow – Integração / Integration
O projeto utiliza **MLflow Tracking** e **MLflow Models** para:  
The project uses **MLflow Tracking** e **MLflow Models** para:  
- Registro automático de parâmetros, métricas e artefatos / Automatic logging of parameters, metrics, and artifacts  
- Padronização de modelos para deployment / Standardized model packaging for deployment  
- Comparação de experimentos via MLflow UI / Experiment comparison via MLflow UI  

Exemplo / Example:
```python
import mlflow

with mlflow.start_run():
    mlflow.log_param('model_type', 'RandomForest')
    mlflow.log_metric('accuracy', 0.92)
    mlflow.sklearn.log_model(model, 'model')
```

---

## ▶️ Como Executar / How to Run

👉 **Para um guia completo de implantação e teste de toda a solução (Minikube, Kubernetes, MLflow, FastAPI, Prometheus, Grafana e Streamlit), consulte:**
*   [docs/usage/usage_pt.md#guia-completo-implantação-e-teste-da-solução](docs/usage/usage_pt.md#guia-completo-implantação-e-teste-da-solução)
*   [docs/usage/usage_en.md#comprehensive-guide-solution-deployment-and-testing](docs/usage/usage_en.md#comprehensive-guide-solution-deployment-and-testing)

### Instalação / Installation
```bash
# create a Python virtual environment and activate it
python -m venv .venv
source .venv/bin/activate

# clone repository and install dependencies
git clone https://github.com/FGalvao77/end-to-end-mlflow-project.git
cd end-to-end-mlflow-project

# install package in editable mode and then dependencies
pip install -e .
pip install -r requirements.txt
# the `-e` flag makes `mlops_project` importable by tests and scripts
``` 

> 📁 toda a documentação adicional foi movida para a pasta `docs/` (Ex.: `docs/usage/`).

### Pipeline
```bash
# run project modules using the installed package or by invoking the module path
python -m mlops_project.data_preprocessing    # data preparation
python -m mlops_project.train                 # training and logging
python -m mlops_project.evaluate              # evaluation reports
python -m mlops_project.deploy                # model export / packaging
```

### Running the test suite
The repository includes simple unit tests for training, evaluation and
deployment logic.  To execute them (from the project root) run:

```bash
.venv/bin/python -m pytest -q
```

The helper `train.train_model()` used by the tests sets up an isolated
file‑based tracking store so the tests never require an MLflow server and
don't leave garbage behind.

### MLflow UI
By default the training script uses a **file-based tracking store** located
inside the project (`mlruns/`).  This means you can run the pipeline without
having an MLflow server running and you won't see any connection errors
(see `src/mlops_project/train.py` for details).

If you prefer to run an MLflow server inside Docker you can use the
provided compose file.  Start it after you have activated your virtual
environment:

```bash
export DOCKER_API_VERSION=1.44
docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d
```

The UI (when started via the provided compose file) will be available at **`http://127.0.0.1:5001`** (NOT `http://0.0.0.0:5000` 
which doesn't work in browsers). You can also point the code at a remote 
tracking server by setting `MLFLOW_TRACKING_URI` in your environment:

```bash
# Access MLflow UI in browser (compose mapping uses host port 5001):
http://127.0.0.1:5001        # ✓ Localhost (recommended)
http://localhost:5001        # ✓ Hostname alias

# Point training code to MLflow server (from host, when using compose):
export MLFLOW_TRACKING_URI=http://127.0.0.1:5001  # From host
# OR inside container:
export MLFLOW_TRACKING_URI=http://mlflow:5000     # Docker network
```

If you prefer to use the standalone server or view experiments through the
web UI, start it in the project root before running `train.py`:

```bash
mlflow ui
```

The UI will be available at `http://127.0.0.1:5000` unless you override the
port.  You can also point the code at a remote tracking server by setting
`MLFLOW_TRACKING_URI` in your environment, e.g.: 

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
```

<h3>Handling corrupted tracking stores</h3>
The training script now automatically cleans up any non‑numeric subdirectories
under `mlruns/` at startup – these are usually created when the
`MLFLOW_ARTIFACT_URI` was mis‑configured and they can lead to warnings or
failures such as the ``MissingConfigException`` shown above.  If you ever
experience errors during MLflow logging you can safely remove the entire
``mlruns/`` directory:

```bash
rm -rf mlruns
```

Additionally the script prints warnings and continues if it is unable to log a
model (e.g. due to a missing ``meta.yaml`` or permission error), so training
itself will not abort just because of MLflow issues.

> **Tip:** you can inspect the output for messages prefixed with ``WARNING:``
> to understand why MLflow logging may have failed; these will not stop the
> pipeline from producing artifacts in the `artifacts/` folder.

<h3>Running Training with Remote MLflow Server</h3>

When you run training against a **remote MLflow server** (HTTP), you may encounter
a `Permission denied: '/mlruns'` error. This happens because:

1. The client (training script running on the **host**) tries to write artifacts directly to paths like `/mlruns`
2. The MLflow server runs in a **Docker container** and `/mlruns` is a container-internal path
3. The host OS cannot access container-internal paths

<h4>Solution 1: Run training INSIDE the Docker container (Recommended)</h4>

Run training from within the container where paths are consistent:

```bash
# Start the MLflow server first
export DOCKER_API_VERSION=1.44
docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d mlflow

# Wait for server to be ready (30-40 seconds) then run training inside container
docker compose -f src/mlops_project/docker-compose.mlflow.yml exec training python train.py
```

<h4>Solution 2: Use file-based tracking (No server required)</h4>

Simply don't set `MLFLOW_TRACKING_URI` - the script defaults to a local file store:

```bash
# Just run training without server
.venv/bin/python src/mlops_project/train.py

# View experiments in the UI
mlflow ui

# Se houver mensagem de erro, como:

ERROR: [Errno 98] Adress already in use

# 1⁰ Verifique que processo está usando o 5000 (ou a porta que você especificou):
lsof -i :5000
# ou
ss -ltnp | grep 5000

# 2⁰ Mate o processo (no exemplo abaixo o PID é 12345):
kill 12345
# se não encerrar:
kill -9 12345

# 3⁰ Reinicie a UI opcionalmente indicando outra porta se preferir:
mlflow ui --port 5001
```

<h3>Running the built image (examples)</h3>

Start the MLflow tracking server from the image (host port 5001 -> container 5000):

```bash
# start mlflow server
docker run --rm --name mlflow_local -p 5001:5000 \
    -v "$(pwd)/mlruns":/mlruns:rw \
    -e MLFLOW_BACKEND_STORE_URI=sqlite:////mlruns/mlflow.db \
    -e MLFLOW_DEFAULT_ARTIFACT_ROOT=file:///mlruns/artifacts \
    my-mlflow-app:latest
```

Serve a saved MLflow model (host 8000 -> container 8000). Set `SERVE_MODEL=1` and `SERVE_MODEL_PATH`:

```bash
# serve model from project artifacts
docker run --rm --name model_server -p 8000:8000 \
    -v "$(pwd)/artifacts/model":/model:ro \
    -e SERVE_MODEL=1 -e SERVE_MODEL_PATH=/model \
    my-mlflow-app:latest
```

Check endpoints:

```bash
curl -s http://127.0.0.1:5001/health   # MLflow server
curl -s http://127.0.0.1:8000/ping     # model server
```

<h3>Deploying to Kubernetes</h3>

<h4>⚠️ Prerequisite: Minikube must be running</h4>

Before deploying to Kubernetes, you need an active cluster. The simplest way is via **Minikube**:

```bash
# Check if Minikube is running
minikube status

# If not, start it
minikube start

# Verify kubectl connectivity
kubectl cluster-info
kubectl get nodes
```

<h4>Deploy to Kubernetes</h4>

The project includes Kubernetes manifests for production-ready deployment:

```bash
# Deploy to Kubernetes cluster (default: Minikube)
kubectl apply -f k8s/mlflow-deployment.yaml

# Check status
kubectl get all -n mlflow-prod

# For detailed K8s setup, troubleshooting, and CI/CD integration see k8s/README.md
```

**Quick Kubernetes Commands:**
```bash
# Port-forward for local access (Minikube)
kubectl port-forward svc/mlflow-service -n mlflow-prod 5000:5000 &
kubectl port-forward svc/model-service -n mlflow-prod 8000:8000 &

# View MLflow UI: http://localhost:5000
# Model Server: http://localhost:8000/ping

# Scale model server
kubectl scale deployment model-server -n mlflow-prod --replicas=5

# Remove all K8s resources
kubectl delete namespace mlflow-prod
```

See [k8s/README.md](k8s/README.md) for:
- Full installation guide (kubectl, Minikube, cloud clusters)  
- Image registry setup (Docker Hub, ECR, GCR)  
- Monitoring, scaling, and troubleshooting  
- CI/CD automation examples  

<h4>Solution 3: Configure S3-compatible artifact store (Production)</h4>

For production, use a cloud artifact store (S3, MinIO, etc.) instead of file system:

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
export MLFLOW_DEFAULT_ARTIFACT_ROOT=s3://my-bucket/mlflow-artifacts

# Or for MinIO (S3-compatible):
export MLFLOW_ARTIFACT_ROOT_BUCKET=mlflow
export AWS_ACCESS_KEY_ID=minioadmin
export AWS_SECRET_ACCESS_KEY=minioadmin

.venv/bin/python src/mlops_project/train.py
```

---

<h2> 📊 Monitoramento e Observabilidade / Monitoring & Observability</h2>

<h3>Prometheus + Grafana Stack</h3>

This project includes a complete monitoring solution using **Prometheus** and **Grafana** for observability of MLflow and model serving infrastructure.

O projeto inclui uma solução completa de monitoramento usando **Prometheus** e **Grafana** para observabilidade da infraestrutura MLflow e model serving.

<h4>Quick Start</h4>

```bash
# Deploy monitoring stack
kubectl apply -f k8s/monitoring/prometheus-config.yaml
kubectl apply -f k8s/monitoring/prometheus-grafana-deployment.yaml

# Access Prometheus (port-forward)
kubectl port-forward svc/prometheus -n mlflow-prod 9090:9090
# → http://127.0.0.1:9090

# Access Grafana (port-forward)
kubectl port-forward svc/grafana -n mlflow-prod 3000:3000
# → http://127.0.0.1:3000 (admin / admin123456789)
```

<h4>Key Features</h4>

**Real-time Metrics:**
- MLflow server health and performance
- Model serving inference latency and throughput
- Kubernetes pod and node metrics
- HTTP request rates, errors, and latencies

**Pre-configured Dashboards:**
- MLflow & Model Server Monitoring (request rates, latencies, success rates)
- Kubernetes cluster health and resource utilization
- Custom PromQL queries for detailed analysis

**Alert Rules:**
- Critical: Server downtime, pod crashes, high error rates
- Warning: High CPU/memory usage, model latency spikes, training failures

<h4>Components</h4>

| Component | Port | Purpose |
|-----------|------|---------|
| **Prometheus** | 9090 (NodePort: 30090) | Metrics collection, storage, alerting rules |
| **Grafana** | 3000 (NodePort: 30300) | Metrics visualization, dashboards, alerts |

<h4>Scrape Targets</h4>

Prometheus automatically scrapes metrics from:
- Prometheus itself: `http://prometheus:9090`
- MLflow server: `http://mlflow-service:5000/metrics`
- Model server: `http://model-service:8000/metrics`
- Kubernetes API, nodes, and pods (service discovery)

<h4>Example Queries</h4>

**MLflow Request Health:**
```promql
sum(rate(http_requests_total{job="mlflow-server", status="200"}[5m])) by (path)
```

**Model Inference Latency (p95):**
```promql
histogram_quantile(0.95, rate(mlflow_model_request_duration_seconds_bucket[5m]))
```

**Pod CPU Usage:**
```promql
sum(rate(container_cpu_usage_seconds_total{namespace="mlflow-prod"}[5m])) by (pod)
```

<h4>For Detailed Configuration</h4>

See [monitoring/README.md](monitoring/README.md) for:
- Complete setup guide (Kubernetes, Minikube, cloud)
- Dasboard creation and customization
- PromQL query examples
- Troubleshooting
- Performance tuning
- Alert configuration

---

<h2> 🚀 FastAPI REST API for Model Serving</h2>

This project includes a **production-ready FastAPI application** for serving machine learning model predictions via REST endpoints. The API is fully integrated with **Prometheus metrics**, **health checks**, and **batch prediction support**.

O projeto inclui uma **aplicação FastAPI pronta para produção** para servir previsões de modelos de machine learning através de endpoints REST. A API é totalmente integrada com **métricas Prometheus**, **health checks** e **suporte para previsões em lote**.

<h3>Architecture</h3>

```
┌─────────────────────────────────────────────────────────┐
│         FastAPI Application (api.py)                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Endpoints:                                       │  │
│  │  - /health, /ping               [Health Checks]  │  │
│  │  - /model/metadata, /features   [Model Info]     │  │
│  │  - /predict                     [Single Pred]    │  │
│  │  - /batch-predict               [Batch Pred]     │  │
│  │  - /invocations                 [MLflow Compat]  │  │
│  │  - /metrics, /prometheus-metrics[Prometheus]    │  │
│  └───────────────────────────────────────────────────┘  │
│                       ↓                                   │
│          Load Model on Startup (artifacts/)              │
│                       ↓                                   │
│         Pydantic Validation (schemas.py)                 │
│                       ↓                                   │
│     Prometheus Metrics (counters, histograms, gauges)    │
└─────────────────────────────────────────────────────────┘
```

<h3>Quick Start (Docker)</h3>

**Start the API server:**

```bash
# Start with Docker Compose
export DOCKER_API_VERSION=1.44
docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d api

# The API will be available at http://127.0.0.1:8000
```

**Or run standalone (local):**

```bash
# Install FastAPI dependencies (included in requirements.txt)
pip install -r requirements.txt

# Run the API
python -m uvicorn src.mlops_project.api:app --host 0.0.0.0 --port 8000

# The API will be available at http://127.0.0.1:8000
```

<h3>Available Endpoints</h3>

<h4>Health Checks & Info (Liveness/Readiness Probes)</h4>

| Method | Endpoint | Purpose | Status Code |
|--------|----------|---------|-------------|
| GET | `/health` | Kubernetes liveness probe | 200 if healthy |
| GET | `/ping` | MLflow compatibility check | 200 if ready |
| GET | `/model/metadata` | Model information (accuracy, F1, classes) | 200 |
| GET | `/model/features` | Expected feature names | 200 |

<h4>Predictions</h4>

| Method | Endpoint | Purpose | Input | Output |
|--------|----------|---------|-------|--------|
| POST | `/predict` | Single prediction | 30 features | Prediction + confidence |
| POST | `/batch-predict` | Batch predictions (1-1000) | Array of features | Array of predictions |
| POST | `/invocations` | MLflow-compatible endpoint | MLflow dataframe_split format | MLflow format response |

<h4>Monitoring & Metrics</h4>

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/metrics` | Prometheus metrics (default format) |
| GET | `/prometheus-metrics` | Prometheus metrics (explicit) |
| GET | `/docs` | Interactive API documentation (Swagger UI) |
| GET | `/redoc` | Alternative API documentation (ReDoc) |

<h3>Example Usage (cURL)</h3>

**1. Health Check**

```bash
curl -X GET http://127.0.0.1:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

**2. Get Model Metadata**

```bash
curl -X GET http://127.0.0.1:8000/model/metadata
```

Response:
```json
{
  "name": "sklearn-model",
  "version": "1.0.0",
  "accuracy": 0.92,
  "f1_score": 0.89,
  "classes": ["class_0", "class_1"],
  "n_features": 30
}
```

**3. Single Prediction**

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "feature_1": 0.5,
    "feature_2": 0.3,
    "feature_3": 0.7,
    ... (30 features total)
  }'
```

Response:
```json
{
  "prediction": 1,
  "probability": [0.08, 0.92],
  "confidence": 0.92,
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

**4. Batch Predictions (Multiple Items)**

```bash
curl -X POST http://127.0.0.1:8000/batch-predict \
  -H "Content-Type: application/json" \
  -d '{
    "records": [
      {
        "feature_1": 0.5,
        "feature_2": 0.3,
        ... (30 features total)
      },
      {
        "feature_1": 0.2,
        "feature_2": 0.8,
        ... (30 features total)
      }
    ]
  }'
```

Response:
```json
{
  "predictions": [
    {
      "prediction": 1,
      "probability": [0.08, 0.92],
      "confidence": 0.92
    },
    {
      "prediction": 0,
      "probability": [0.78, 0.22],
      "confidence": 0.78
    }
  ],
  "processing_time_ms": 45.23,
  "total_records": 2
}
```

**5. Get Metrics (Prometheus format)**

```bash
curl -s http://127.0.0.1:8000/metrics | head -20
```

Output:
```
# HELP prediction_requests_total Total number of prediction requests
# TYPE prediction_requests_total counter
prediction_requests_total{endpoint="predict"} 127
prediction_requests_total{endpoint="batch_predict"} 34

# HELP prediction_latency_seconds Prediction processing latency
# TYPE prediction_latency_seconds histogram
prediction_latency_seconds_bucket{endpoint="predict",le="0.01"} 120
prediction_latency_seconds_bucket{endpoint="predict",le="0.05"} 125
prediction_latency_seconds_bucket{endpoint="predict",le="0.1"} 127
```

<h3>Interactive API Documentation</h3>

Once the API is running, access the interactive documentation:

- **Swagger UI (Recommended):** http://127.0.0.1:8000/docs
- **ReDoc (Alternative):** http://127.0.0.1:8000/redoc

These interfaces allow you to:
- Browse all available endpoints
- View request/response schemas
- Test endpoints directly in the browser
- See real-time responses

<h3>Deploying to Kubernetes</h3>

The project includes Kubernetes manifests for the FastAPI API:

```bash
# Deploy FastAPI API to Kubernetes
kubectl apply -f k8s/fastapi-deployment.yaml

# Check status
kubectl get all -n mlflow-prod

# Port-forward for local access
kubectl port-forward svc/fastapi-service -n mlflow-prod 8000:8000 &

# Access the API
curl http://localhost:8000/health
```

**Kubernetes Configuration Includes:**
- Deployment with auto-scaling (2-5 replicas)
- Service (NodePort: 30800 for external access)
- Health checks (liveness & readiness probes)
- Resource limits and requests
- Environment variables for configuration

<h3>Monitoring the API (Prometheus + Grafana)</h3>

The FastAPI application exposes metrics compatible with Prometheus. Track:

- **Request volume:** `sum(rate(prediction_requests_total[5m]))`
- **Error rate:** `sum(rate(prediction_requests_failed[5m]))`
- **Latency (p95):** `histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m]))`
- **Model load status:** `model_loaded` (gauge)
- **Uptime:** `api_uptime_seconds` (gauge)

**View metrics in Grafana:**
1. Access Grafana: http://127.0.0.1:3000 (port-forwarded)
2. Dashboard: "API Metrics" shows FastAPI performance
3. Alerts trigger if error rate > 5% or latency > 500ms

<h3>API Configuration</h3>

**Environment Variables:**

| Variable | Default | Purpose |
|----------|---------|---------|
| `API_PORT` | 8000 | Port the API listens on |
| `MODEL_PATH` | `artifacts/model/model.joblib` | Path to trained model |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `SERVE_API` | (set by docker-compose) | Enable API mode in Docker entrypoint |

**Model Requirements:**
- Must be a scikit-learn model (joblib-serialized)
- Must accept 30 input features
- Must support `.predict()` and `.predict_proba()` methods

<h3>Error Handling</h3>

**400 Bad Request:** Invalid input (wrong number of features, missing fields)
```json
{
  "error": "Validation error",
  "details": "Expected 30 features, got 29"
}
```

**404 Not Found:** Model not loaded
```json
{
  "error": "Model not available",
  "details": "Model file not found at artifacts/model/model.joblib"
}
```

**500 Internal Server Error:** Server error
```json
{
  "error": "Internal server error",
  "details": "Model prediction failed"
}
```

<h3>Performance Testing</h3>

```bash
# Test single prediction latency
time curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d "@sample_request.json"

# Load test with Apache Bench
ab -n 1000 -c 10 -p sample_request.json \
  -T application/json http://127.0.0.1:8000/predict

# Load test with wrk (concurrent connections)
wrk -t4 -c100 -d30s -s test_predict.lua http://127.0.0.1:8000/predict
```

<h3>For Detailed Information</h3>

See [src/mlops_project/](src/mlops_project/) for:
- `api.py` - FastAPI application with all endpoints
- `schemas.py` - Pydantic request/response models
- `docker-compose.mlflow.yml` - Docker Compose configuration with 'api' service
- `docker-entrypoint.sh` - Smart entrypoint (SERVE_API flag support)

---

<h2> 🖥️ Streamlit Application for Local Prediction</h2>

This project includes an interactive user interface built with **Streamlit** to perform predictions locally in a user-friendly way. Ideal for demonstrations and quick model testing.

<h3>Quick Start (Local)</h3>

**1. Installation:**

```bash
# Create and activate a virtual environment (if you haven't already)
python -m venv .venv
source .venv/bin/activate

# Install dependencies (including Streamlit)
pip install -r requirements.txt
```

**2. Train the Model (if you haven't already):**

```bash
# Run the training script to generate the model and metadata
python -m mlops_project.train
```

**3. Run the Streamlit Application:**

```bash
streamlit run src/mlops_project/streamlit_app.py
```

The application will automatically open in your browser at `http://localhost:8501`.

<h3>Features</h3>

-   **User-Friendly Interface:** Inputs for the 30 model features.
-   **Real-time Predictions:** Submit values to get the prediction (benign/malignant) and probabilities.
-   **Random Feature Generation:** Button to populate fields with random values for quick testing.
-   **Dynamic Loading:** Loads the model and its metadata (`metadata.json`) dynamically, ensuring the interface reflects the trained model.

---

<h2> Guia Completo: Implantação e Teste da Solução</h2>

Este guia consolida todos os passos para iniciar o ambiente completo do projeto, desde o Minikube até a visualização de todas as aplicações no navegador.

<h3>Pré-requisitos (Verificação Rápida)</h3>

*   **Minikube:** Instalado e `kubectl` configurado.
*   **Docker Desktop:** Instalado e em execução (ou ambiente Docker compatível).
*   **Dependências Python:** `pip install -r requirements.txt` já executado em um ambiente virtual ativo.

<h3>1. Iniciar o Minikube</h3>

```bash
minikube start --driver=docker # Ou o driver de sua preferência
```
Aguarde até que o Minikube esteja totalmente inicializado (`minikube status` deve mostrar `Running`).

<h3>2. Preparar Imagem Docker do Projeto</h3>

```bash
# Configure o ambiente Docker para apontar para o daemon do Minikube
eval $(minikube docker-env)

# Construa a imagem Docker do seu projeto (será usada pelos Deployments no K8s)
docker build -t my-mlflow-app:latest -f src/mlops_project/Dockerfile .

# Opcional: Volte o ambiente Docker para o seu daemon local (se você tiver um)
eval $(minikube docker-env -u)
```

<h3>3. Gerar Artefatos do Modelo (Treinamento Local)</h3>

Execute o script de treinamento para gerar o modelo serializado (`model.joblib`) e os metadados (`metadata.json`) que as aplicações utilizarão.

```bash
python -m mlops_project.train
```

<h3>4. Implantar Componentes no Kubernetes</h3>

Aplique os manifestos do Kubernetes para implantar o MLflow Server, a API FastAPI e o stack de Monitoramento (Prometheus e Grafana).

```bash
# Implante o MLflow Server e a API FastAPI
kubectl apply -f k8s/mlflow-deployment.yaml
kubectl apply -f k8s/fastapi-deployment.yaml

# Implante o Stack de Monitoramento
chmod +x scripts/monitoring.sh # Garanta que o script é executável
./scripts/monitoring.sh deploy
```
Aguarde alguns minutos e verifique o status dos pods até que todos estejam `Running` ou `Completed` no namespace `mlflow-prod`:
```bash
kubectl get pods -n mlflow-prod
```

<h3>5. Configurar Acesso Local (Port-Forwarding)</h3>

Abra **novas abas/janelas do terminal** para cada comando de `port-forward` ou use `&` para rodar em segundo plano e ter acesso a todas as interfaces simultaneamente.

```bash
# Para o MLflow UI
kubectl port-forward svc/mlflow-service -n mlflow-prod 5000:5000 &

# Para a API FastAPI
kubectl port-forward svc/fastapi-service -n mlflow-prod 8000:8000 &

# Para Prometheus e Grafana (usando o script helper)
./scripts/monitoring.sh port-forward &
```
Aguarde alguns segundos para que os `port-forwards` estabeleçam a conexão.

<h3>6. Acesse as Aplicações no Navegador</h3>

Agora você pode acessar todas as interfaces e testar a solução completa!

*   **MLflow UI:**
    *   URL: `http://127.0.0.1:5000`
    *   Visualize os experimentos, parâmetros e métricas do treinamento.

*   **FastAPI Swagger UI (Documentação Interativa):**
    *   URL: `http://127.0.0.1:8000/docs`
    *   Explore os endpoints da API, faça requisições de teste e veja a estrutura das respostas.
    *   Para um quick check do status da API: `http://127.0.0.1:8000/health`

*   **Prometheus:**
    *   URL: `http://127.0.0.1:9090`
    *   Verifique os "Targets" para confirmar se o Prometheus está coletando métricas dos serviços MLflow e FastAPI.

*   **Grafana:**
    *   URL: `http://127.0.0.1:3000`
    *   **Credenciais:** `admin` / `admin123456789`
    *   Acesse o dashboard pré-configurado **"MLflow & Model Server Monitoring"** para visualizar as métricas de desempenho.

*   **Streamlit Application (Rodando Localmente):**
    *   Em um terminal onde seu ambiente virtual está ativo (`source .venv/bin/activate`), execute:
        ```bash
        streamlit run src/mlops_project/streamlit_app.py
        ```
    *   A aplicação abrirá automaticamente no seu navegador, geralmente em `http://localhost:8501`. Interaja com os campos, gere valores aleatórios e faça predições.

<h3>7. Limpeza (Opcional)</h3>

Para remover todos os componentes do Kubernetes e parar o Minikube após os testes:

```bash
# Remova os deployments e serviços do MLflow e FastAPI
kubectl delete -f k8s/mlflow-deployment.yaml
kubectl delete -f k8s/fastapi-deployment.yaml

# Limpe o stack de monitoramento
./scripts/monitoring.sh cleanup

# Pare o Minikube
minikube stop

# Opcional: Exclua o cluster Minikube
# minikube delete
```

---

<h2> ✅ Boas Práticas / Best Practices</h2>
- Estrutura modular e escalável / Modular and scalable structure  
- Clean versioning with `.gitignore` / Clean versioning with `.gitignore`  
- Registro completo de experimentos com MLflow / Complete experiment tracking with MLflow  
- Separação clara entre **ETL, treinamento, avaliação e deployment** / Clear separation of **ETL, training, evaluation, and deployment**  
- Documentação técnica voltada para recrutadores / Technical documentation tailored for recruiters
- **Clean Code & Consistência:** Código refatorado para maior clareza, menos hardcoding e carregamento dinâmico de metadados do modelo.
- **Dynamic Model Metadata:** FastAPI e Streamlit agora carregam metadados do modelo (`metadata.json`) e nomes de features dinamicamente, reduzindo a chance de inconsistências.

---

<h2> 🔮 Extensões Futuras / Future Extensions</h2>
- Integração com **Docker/Kubernetes** / Integration with **Docker/Kubernetes**  
- Automação de pipeline com **CI/CD (GitHub Actions)** / Pipeline automation with **CI/CD (GitHub Actions)**  
- Monitoramento de modelos em produção / Model monitoring in production  
- Inclusão de testes unitários e integração contínua / Unit testing and continuous integration  
- **MLflow Model Registry:** Integrar a gestão de versões e estágios do modelo via MLflow Model Registry para rastreamento completo do ciclo de vida.
- **Data Drift Monitoring:** Add components to monitor data drift in production and alert on potential performance degradations.

---

<h2> 📌 Conclusão / Conclusion</h2>
Este projeto exemplifica um pipeline moderno de **MLOps**, destacando:  
This project exemplifies a modern **MLOps pipeline**, highlighting:  
- **Rigor técnico / Technical rigor**  
- **Boas práticas de engenharia / Engineering best practices**  
- **Capacidade de deployment real / Real deployment capability**  

👉 Ele serve como uma vitrine para recrutadores, demonstrando experiência prática em **Machine Learning aplicado a produção**.  
👉 It serves as a showcase for recruiters, demonstrating practical experience in **Machine Learning applied to production**.

---
