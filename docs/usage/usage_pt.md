# Step-by-Step Project Implementation

---

## ⚡ Important Tips (Read First!)

### 📁 No Need to Change Directories

With the project as an **editable Python package** (`pip install -e .`), run everything **from the project root**:

```bash
cd /your-paths/end-to-end-mlflow-project
python -m mlops_project.train      # works from here
python -m pytest tests/             # works from here
kubectl apply -f k8s/...          # works from here
```

**Only enter specific folders if you want to edit code** (`src/mlops_project/`) **or read docs** (`docs/`).

---

### 🐳 Cleaning Up Docker Containers

If you get `"container name is already in use"` error, remove the old one:

```bash
# Remove a specific container
docker rm -f model_server

# Or clean all stopped containers
docker container prune -f
```

---

### 🌐 "404 Not Found" Error on `/favicon.ico`

Perfectly normal! The browser tries to load the tab icon, which doesn't exist.

✅ **The endpoint still worked** — use `curl` to see the response:

```bash
curl -s http://127.0.0.1:8000/ping
```

Or access the **Swagger UI** (interactive API docs):

```
http://127.0.0.1:8000/docs
```

---

### ☸️ Essential Kubernetes Commands

```bash
# Deploy
kubectl apply -f k8s/mlflow-deployment.yaml

# Check status
kubectl get pods
kubectl get svc
kubectl rollout status deploy/mlflow-server

# Port-forward (access locally)
kubectl port-forward svc/mlflow-service -n mlflow-prod 5000:5000
kubectl port-forward svc/model-service -n mlflow-prod 8000:8000

# View logs
kubectl logs -l app=mlflow-server --tail=100
```

---

## ⚙️ System Prerequisites

### Kubernetes & Minikube (required for deployment)

Before running any `kubectl` commands, you need an active Kubernetes cluster. The simplest way is via **Minikube**.

#### Install Minikube

**macOS:**
```bash
brew install minikube
mkdir -p ~/.minikube
```

**Linux:**
```bash
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**Windows:**
```bash
choco install minikube
# or manual download: https://github.com/kubernetes/minikube/releases
```

#### Start Minikube

```bash
# Start cluster (may take a few minutes on first run)
minikube start

# Check status
minikube status

# Verify Kubernetes connectivity
kubectl cluster-info
kubectl get nodes
```

When all statuses are `Running` or return information, Kubernetes is ready! ✅

#### Stop/Reset Minikube

```bash
# Stop (preserves data)
minikube stop

# Reset (cleans everything)
minikube delete
minikube start  # starts new cluster
```

---

## 0) Overview of What Already Exists

- **Training**: `train.py` trains a `RandomForest` inside a `Pipeline` with `StandardScaler`, computes metrics, saves artifacts in `artifacts/model` and (if available) logs to MLflow.  
- **Config**: `configs.yaml` defines `test_size`, `random_state`, hyperparameters and export folder.  
- **Data**: `data_prep.py` uses scikit-learn's `load_breast_cancer` and performs a stratified split.  
- **Util**: `utils.py` loads YAML (the function `load_config`).  
- **Tracking**: `docker-compose.mlflow.yml` brings up a file‑based MLflow Server on port 5000.  
- **Kubernetes**: `deployment.yaml` defines a Deployment/Service for the image `projeto10-model:latest` (port 8000, `/ping`, NodePort 30080).

---

## 1) Prepare Local Environment

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -U pip

# install project dependencies
pip install -r requirements.txt 
or
pip install -qU -r requirements.txt

# (optional) MLflow for tracking/serving
export DOCKER_API_VERSION=1.44
# Run MLflow tracking server from image (host 5001 -> container 5000):
docker run --rm --name mlflow_local -p 5001:5000 \
  -v "$(pwd)/mlruns":/mlruns:rw \
  -e MLFLOW_BACKEND_STORE_URI=sqlite:////mlruns/mlflow.db \
  -e MLFLOW_DEFAULT_ARTIFACT_ROOT=file:///mlruns/artifacts \
  my-mlflow-app:latest

# Serve a saved MLflow model from project artifacts (host 8000 -> container 8000):
docker run --rm --name model_server -p 8000:8000 \
  -v "$(pwd)/artifacts/model":/model:ro \
  -e SERVE_MODEL=1 -e SERVE_MODEL_PATH=/model \
  my-mlflow-app:latest

# Check endpoints:
curl -s http://127.0.0.1:5001/health   # MLflow server
curl -s http://127.0.0.1:8000/ping     # model server
> The package is importable via `python -m mlops_project.<module>`; you no longer need to change directories.
```

---

## 2) Inspect and Adjust `configs.yaml`

Open `src/mlops_project/configs.yaml` and modify as needed (it comes with default values):  
- `test_size`, `random_state`  
- `model.params` (e.g. `n_estimators`, `max_depth`, `n_jobs`)  
- `paths.exported_model_dir` (e.g. `artifacts/model`)  

---

## 3) Run Training and Generate Artifacts

The dataset comes from `load_breast_cancer(as_frame=True)` and the split is stratified.  

From the repository root execute the module directly:

```bash
python -m mlops_project.train
```

Execution flow:
- Load config (`utils.load_config`) and data (`data_prep.load_dataset`).  
- Train/test split using `test_size` and `random_state` from the YAML.  
- Build `Pipeline([('scaler', StandardScaler(with_mean=False)), ('clf', RandomForestClassifier(**params))])`, train, predict and compute **accuracy**, **precision**, **recall**, **f1**, also printing the `classification_report`.  
- Create `artifacts/model` folder (or the one from YAML) and save `model.joblib`.  
- If MLflow is installed/imported, save an **MLflow Model** in the same directory and log **parameters/metrics/model** to the server (if `MLFLOW_TRACKING_URI` is configured).  

---

## 4) Start the MLflow Tracking Server

Videos on installing Docker and Docker Compose:

https://www.youtube.com/watch?v=05YN8F8ajBc&t=10s  (Windows)

https://www.youtube.com/watch?v=h27ZVQIh7Ro (docker compose on Linux)

https://www.youtube.com/watch?v=Gpal5KsSHMQ&t=1s (docker on Linux)

Bring up the server with the compose file you already have:

```bash 
export DOCKER_API_VERSION=1.44
docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d     

# Or you can append "mlflow" at the end of the command
eport DOCKER_API_VERSION=1.44
docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d mlflow
 
 # UI at http://localhost:5000
```

In the terminal where you will train, point the client to the server and (optionally) set the experiment name:

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
export MLFLOW_EXPERIMENT_NAME=Projeto10_MLOps
```

> Rerun **step 3** to log runs, parameters, metrics and the model to MLflow. `train.py` is already prepared for this.

---

## 5) Serve the Model Locally (MLflow Models Serve)

Since `train.py` saves an **MLflow Model** inside the export folder, you can serve it directly:

```bash
mlflow models serve   -m artifacts/model   -p 8000 --host 0.0.0.0 --no-conda
```

### Quick Tests

```bash
# healthcheck (compatible with /ping in your manifest)
curl -s http://127.0.0.1:8000/ping

# inference
curl -X POST http://127.0.0.1:8000/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "dataframe_split": {
      "columns": [
        "mean radius","mean texture","mean perimeter","mean area","mean smoothness",
        "mean compactness","mean concavity","mean concave points","mean symmetry","mean fractal dimension",
        "radius error","texture error","perimeter error","area error","smoothness error",
        "compactness error","concavity error","concave points error","symmetry error","fractal dimension error",
        "worst radius","worst texture","worst perimeter","worst area","worst smoothness",
        "worst compactness","worst concavity","worst concave points","worst symmetry","worst fractal dimension"
      ],
      "data": [[
        14.0,20.0,90.0,600.0,0.10,
        0.15,0.12,0.07,0.18,0.06,
        0.4,1.2,3.0,40.0,0.01,
        0.02,0.03,0.02,0.03,0.004,
        16.5,27.0,110.0,850.0,0.13,
        0.25,0.22,0.12,0.24,0.08
      ]]
    }
  }'
'
```

> Tip: if you prefer, save the MLflow Model in a **subdirectory** (e.g. `artifacts/model/mlflow_model`) to avoid mixing with `model.joblib`.

---

## 6) Package the Application in Docker

The image expected by your K8s `Deployment` is named **`projeto10-model:latest`** and exposes **port 8000** with a **`/ping`** endpoint.

Build the image using the Dockerfile:

```bash
export DOCKER_API_VERSION=1.44
docker build -t my-mlflow-app:latest -f src/mlops_project/Dockerfile .
```

Test locally:

```bash
export DOCKER_API_VERSION=1.44
docker run --rm -p 8000:8000 my-mlflow-app:latest
curl -s http://127.0.0.1:8000/ping
```

---

## 7) Deploy on Kubernetes
### ⚠️ Prerequisite: Minikube must be running

Before executing the commands below, make sure Minikube is active:

```bash
minikube status
# Must show: host: Running, kubelet: Running, apiserver: Running
```

If not, run:
```bash
minikube start
```

### Deploy
Apply the manifests you already have:

https://www.youtube.com/watch?v=mi_aotXDMR8 (how to install Kubernetes - kubectl)

```bash
kubectl apply -f k8s/mlflow-deployment.yaml
kubectl get pods
kubectl get svc
kubectl get deploy mlflow-server
kubectl rollout status deploy/mlflow-server
kubectl get pods -l app=mlflow-server -o wide
kubectl logs -l app=mlflow-server --tail=100
```

- **Deployment**: 2 replicas, `image: my-mlflow-app:latest`, health checks on `/health` port 5000.  
- **Service**: type **NodePort**, exposing **30500** on the node.

### Tests

```bash
# if NodePort and you're on the same node (minikube/kind):
curl -s http://127.0.0.1:30500/health

# or port-forward
kubectl port-forward svc/mlflow-service -n mlflow-prod 5000:5000
kubectl port-forward svc/model-service -n mlflow-prod 8000:8000
curl -s http://127.0.0.1:5000/health

# inference
curl -X POST http://127.0.0.1:8000/invocations \
  -H "Content-Type: application/json" \
  -d '{"dataframe_split":{"columns":["mean radius","mean texture","mean perimeter"],"data":[[14.0,20.0,90.0]]}}'
```

---

## 8) Monitoramento e Observabilidade / Monitoring & Observability

**Versão em Português:**

Implante monitoramento e observabilidade abrangentes usando **Prometheus** e **Grafana** para rastrear o servidor MLflow e a infraestrutura de serving de modelos.

### ⚠️ Pré-requisito: Minikube rodando

Os mesmos comandos acima.

### 8.1) Deploy Prometheus & Grafana Stack

```bash
# Deploy Prometheus configuration and alert rules
kubectl apply -f k8s/monitoring/prometheus-config.yaml

# Deploy Prometheus and Grafana services
kubectl apply -f k8s/monitoring/prometheus-grafana-deployment.yaml

# Verify deployment
kubectl get all -n mlflow-prod
kubectl get pods -n mlflow-prod | grep -E "prometheus|grafana"
```

### 8.2) Acessar Prometheus

**Via Port-Forward (recomendado para desenvolvimento):**
```bash
kubectl port-forward svc/prometheus -n mlflow-prod 9090:9090
# → acessar: http://127.0.0.1:9090
```

**Via Minikube Service:**
```bash
minikube service prometheus -n mlflow-prod
```

**Verificar Targets de Scrape:**
```bash
curl -s http://127.0.0.1:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, instance: .labels.instance, state: .health}'

# Expected UP targets:
# - prometheus
# - mlflow-server
# - model-server
```

### 8.3) Acessar Grafana

**Via Port-Forward:**
```bash
kubectl port-forward svc/grafana -n mlflow-prod 3000:3000
# → acessar: http://127.0.0.1:3000
```

**Via Minikube Service:**
```bash
minikube service grafana -n mlflow-prod
```

**Login Padrão:**
- **Usuário:** `admin`
- **Senha:** `admin123456789`

### 8.4) Visualizar Dashboard Pré‑configurado

O dashboard é provisonado automaticamente via ConfigMap:

1. Faça login no Grafana (http://127.0.0.1:3000)
2. Clique em **Dashboards** → **MLflow & Model Server Monitoring**
3. Veja métricas em tempo real:
   - Status do servidor MLflow e latência de requisições
   - Taxa de requisições e taxa de erros do servidor de modelos
   - Métricas de pods e nós do Kubernetes

**Importação Manual do Dashboard (se não for provisionado):**
```bash
# Copy dashboard JSON
kubectl create configmap grafana-dashboard-mlflow \
  --from-file=k8s/monitoring/dashboards/mlflow-monitoring-dashboard.json \
  -n mlflow-prod
```

### 8.5) Métricas-chave para monitorar

**Servidor MLflow:**
- Taxa de requisições: `rate(http_requests_total{job="mlflow-server"}[5m])`
- Taxa de erros (4xx, 5xx): `rate(http_requests_total{job="mlflow-server",status=~"4..|5.."}[5m])`
- Latência (p95): `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="mlflow-server"}[5m]))`
- Experimentos ativos: `mlflow_experiment_created_total`

**Servidor de Modelos:**
- Taxa de requisições de inferência: `rate(http_requests_total{job="model-server"}[5m])`
- Latência de inferência: `histogram_quantile(0.95, rate(mlflow_model_request_duration_seconds_bucket[5m]))`
- Taxa de erros: `rate(http_requests_total{job="model-server",status=~"4..|5.."}[5m])`
- Predictions/sec: `rate(mlflow_predictions_total[5m])`

**Kubernetes & Sistema:**
- CPU container: `rate(container_cpu_usage_seconds_total{namespace="mlflow-prod"}[5m])`
- Memória container: `container_memory_usage_bytes{namespace="mlflow-prod"}`
- Contagem de pods: `count(kube_pod_info{namespace="mlflow-prod"})`
- CPU de nó: `rate(node_cpu_seconds_total{mode!="idle"}[5m])`

### 8.6) Criar Dashboard Personalizado (Exemplos PromQL)

**Exemplo 1: Taxa de sucesso do MLflow**
```promql
sum(rate(http_requests_total{job="mlflow-server",status="200"}[5m])) / sum(rate(http_requests_total{job="mlflow-server"}[5m])) * 100
```

**Exemplo 2: Throughput de inferência**
```promql
sum(rate(http_requests_total{job="model-server",path="/invocations"}[5m])) by (status)
```

**Exemplo 3: Tendência de uso de memória**
```promql
sum(container_memory_usage_bytes{namespace="mlflow-prod"}) by (pod_name)
```

### 8.7) Visualizar Regras de Alerta

**Checar alertas ativos no Prometheus:**
```bash
curl -s http://127.0.0.1:9090/api/v1/alerts | jq .
```

**Ver alertas na UI do Grafana:**
1. Clique em **Alerts** (ícone de sino) → **Alert rules**
2. Veja estados firing, pending e normal
3. Adicione canais de notificação (Email, Slack, etc.)

**Regras pré-configuradas:**
- `MLflowServerDown`: servidor inacessível (limite 1m)
- `ModelServerDown`: servidor de modelos inacessível (limite 1m)
- `HighCPUUsage`: CPU > 80% por 5 minutos
- `HighMemoryUsage`: memória > 85% por 5 minutos
- `PodCrashLooping`: pod reiniciando frequentemente (5m)
- `HighModelLatency`: latência p95 > 1 segundo

### 8.8) Ajustes de desempenho (opcional)

**Aumentar retenção de métricas (padrão 30 dias):**
```bash
kubectl patch deployment prometheus -n mlflow-prod -p \
  '{"spec":{"template":{"spec":{"containers":[{"name":"prometheus","args":["--storage.tsdb.retention.time=365d"]}]}}}}'
```

**Reduzir cardinalidade (alto consumo de memória):**
Edite `k8s/monitoring/prometheus-config.yaml` e adicione relabeling:
```yaml
metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'node_(network|netdev).*'
    action: drop  # Descarte métricas com alta cardinalidade
```

**Aumentar recursos do Prometheus:**
```yaml
resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 2Gi
```

### 8.9) Solução de problemas

**Targets do Prometheus não estão sendo scraping:**
```bash
# Check Prometheus logs
kubectl logs deployment/prometheus -n mlflow-prod --tail=50

# Verify service discovery
curl -s http://127.0.0.1:9090/service-discovery | jq .

# Test connectivity to target
kubectl exec -it deployment/prometheus -n mlflow-prod -- \
  curl -v http://mlflow-service.mlflow-prod.svc.cluster.local:5000/metrics
```

---

## 🖥️ Aplicação Streamlit para Predição Local

A aplicação inclui uma interface de usuário interativa construída com **Streamlit** para realizar predições de forma local e amigável. Ideal para demonstrações e testes rápidos do modelo.

### Início Rápido (Local)

**1. Instalação:**

```bash
# Crie um ambiente virtual e ative-o (se ainda não fez)
python -m venv .venv
source .venv/bin/activate

# Instale as dependências (incluindo Streamlit)
pip install -r requirements.txt
```

**2. Treine o Modelo (se ainda não fez):**

```bash
# Execute o script de treinamento para gerar o modelo e metadados
python -m mlops_project.train
```

**3. Execute a Aplicação Streamlit:**

```bash
streamlit run src/mlops_project/streamlit_app.py
```

A aplicação será aberta automaticamente no seu navegador em `http://localhost:8501`.

### Características

-   **Interface Amigável:** Inputs para as 30 features do modelo.
-   **Predições em Tempo Real:** Submeta os valores para obter a predição (benigno/maligno) e as probabilidades.
-   **Geração Aleatória de Features:** Botão para preencher os campos com valores aleatórios para testes rápidos.
-   **Carregamento Dinâmico:** Carrega o modelo e seus metadados (`metadata.json`) de forma dinâmica, garantindo que a interface reflita o modelo treinado.

---

## ✅ Boas Práticas / Best Practices
- Estrutura modular e escalável / Modular and scalable structure  
- Versionamento limpo com `.gitignore` / Clean versioning with `.gitignore`  
- Registro completo de experimentos com MLflow / Complete experiment tracking with MLflow  
- Separação clara entre **ETL, treinamento, avaliação e deployment** / Clear separation of **ETL, training, evaluation, and deployment**  
- Documentação técnica voltada para recrutadores / Technical documentation tailored for recruiters
- **Clean Code & Consistência:** Código refatorado para maior clareza, menos hardcoding e carregamento dinâmico de metadados do modelo.
- **Dynamic Model Metadata:** FastAPI e Streamlit agora carregam metadados do modelo (`metadata.json`) e nomes de features dinamicamente, reduzindo a chance de inconsistências.

---

## 🔮 Extensões Futuras / Future Extensions
- Integração com **Docker/Kubernetes** / Integration with **Docker/Kubernetes**  
- Automação de pipeline com **CI/CD (GitHub Actions)** / Pipeline automation with **CI/CD (GitHub Actions)**  
- Monitoramento de modelos em produção / Model monitoring in production  
- Inclusão de testes unitários e integração contínua / Unit testing and continuous integration  
- **MLflow Model Registry:** Integrar a gestão de versões e estágios do modelo via MLflow Model Registry para rastreamento completo do ciclo de vida.
- **Data Drift Monitoring:** Adicionar componentes para monitorar o desvio de dados em produção e alertar sobre potenciais degradações de desempenho.
