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

<h2> 3) Run Training and Generate Artifacts</h2>

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

<h2> 4) Start the MLflow Tracking Server</h2>

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
 
 #UI at http://localhost:5000
```

In the terminal where you will train, point the client to the server and (optionally) set the experiment name:

```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
export MLFLOW_EXPERIMENT_NAME=Projeto10_MLOps
```

> Rerun **step 3** to log runs, parameters, metrics and the model to MLflow. `train.py` is already prepared for this.

---

<h2> 5) Serve the Model Locally (MLflow Models Serve)</h2>

Since `train.py` saves an **MLflow Model** inside the export folder, you can serve it directly:

```bash
mlflow models serve   -m artifacts/model   -p 8000 --host 0.0.0.0 --no-conda
```

<h3>Quick Tests</h3>

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

<h2> 6) Package the Application in Docker</h2>

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

<h2> 7) Deploy on Kubernetes</h2>
<h3>⚠️ Prerequisite: Minikube must be running</h3>

Before executing the commands below, make sure Minikube is active:

```bash
minikube status
# Must show: host: Running, kubelet: Running, apiserver: Running
```

If not, run:
```bash
minikube start
```

<h3>Deploy</h3>
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

<h3>Tests</h3>

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

<h2> 8) Monitoramento e Observabilidade / Monitoring & Observability</h2>

**Versão em Português:**

Implante monitoramento e observabilidade abrangentes usando **Prometheus** e **Grafana** para rastrear o servidor MLflow e a infraestrutura de serving de modelos.

<h3>⚠️ Pré-requisito: Minikube rodando</h3>

Os mesmos comandos acima.

<h3>8.1) Deploy Prometheus & Grafana Stack</h3>

```bash
# Deploy Prometheus configuration and alert rules
kubectl apply -f k8s/monitoring/prometheus-config.yaml

# Deploy Prometheus and Grafana services
kubectl apply -f k8s/monitoring/prometheus-grafana-deployment.yaml

# Verify deployment
kubectl get all -n mlflow-prod
kubectl get pods -n mlflow-prod | grep -E "prometheus|grafana"
```

<h3>8.2) Acessar Prometheus</h3>

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

<h3>8.3) Acessar Grafana</h3>

**Via Port-Forward:**
```bash
kubectl port-forward svc/grafana -n mlflow-prod 3000:3000
# → acessar: http://127.0.0.1:3000
```

**Via Minikube Service:**
```bash
minikube service grafana -n mlflow-prod
```

**Default Login:**
- **Username:** `admin`
- **Password:** `admin123456789`

<h3>8.4) View Pre-built Dashboard</h3>

The dashboard is automatically provisioned via ConfigMap:

1. Login to Grafana (http://127.0.0.1:3000)
2. Click **Dashboards** → **MLflow & Model Server Monitoring**
3. View real-time metrics:
   - MLflow server status and request latency
   - Model server request rate and error rate
   - Kubernetes pod and node metrics

**Manual Dashboard Import (if not provisioned):**
```bash
# Copy dashboard JSON
kubectl create configmap grafana-dashboard-mlflow \
  --from-file=k8s/monitoring/dashboards/mlflow-monitoring-dashboard.json \
  -n mlflow-prod
```

<h3>8.5) Key Metrics to Monitor</h3>

**MLflow Server:**
- Request rate: `rate(http_requests_total{job="mlflow-server"}[5m])`
- Error rate (4xx, 5xx): `rate(http_requests_total{job="mlflow-server",status=~"4..|5.."}[5m])`
- Request latency (p95): `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="mlflow-server"}[5m]))`
- Active experiments: `mlflow_experiment_created_total`

**Model Server:**
- Inference request rate: `rate(http_requests_total{job="model-server"}[5m])`
- Inference latency: `histogram_quantile(0.95, rate(mlflow_model_request_duration_seconds_bucket[5m]))`
- Error rate: `rate(http_requests_total{job="model-server",status=~"4..|5.."}[5m])`
- Predictions/sec: `rate(mlflow_predictions_total[5m])`

**Kubernetes & System:**
- Container CPU: `rate(container_cpu_usage_seconds_total{namespace="mlflow-prod"}[5m])`
- Container Memory: `container_memory_usage_bytes{namespace="mlflow-prod"}`
- Pod count: `count(kube_pod_info{namespace="mlflow-prod"})`
- Node CPU: `rate(node_cpu_seconds_total{mode!="idle"}[5m])`

<h3>8.6) Create Custom Dashboard (PromQL Examples)</h3>

**Example Query 1: MLflow Success Rate**
```promql
sum(rate(http_requests_total{job="mlflow-server",status="200"}[5m])) / sum(rate(http_requests_total{job="mlflow-server"}[5m])) * 100
```

**Example Query 2: Model Inference Throughput**
```promql
sum(rate(http_requests_total{job="model-server",path="/invocations"}[5m])) by (status)
```

**Example Query 3: Memory Usage Trend**
```promql
sum(container_memory_usage_bytes{namespace="mlflow-prod"}) by (pod_name)
```

<h3>8.7) View Alert Rules</h3>

**Check active alerts in Prometheus:**
```bash
curl -s http://127.0.0.1:9090/api/v1/alerts | jq .
```

**Check alerts in Grafana UI:**
1. Click **Alerts** (bell icon) → **Alert rules**
2. View firing, pending and normal states
3. Add notification channels (Email, Slack, etc.)

**Pre-configured Alert Rules:**
- `MLflowServerDown`: Server unreachable (1m threshold)
- `ModelServerDown`: Model server unreachable (1m threshold)
- `HighCPUUsage`: CPU > 80% for 5 minutes
- `HighMemoryUsage`: Memory > 85% for 5 minutes
- `PodCrashLooping`: Pod restarting frequently (5m threshold)
- `HighModelLatency`: p95 latency > 1 second

<h3>8.8) Performance Tuning (Optional)</h3>

**Increase metrics retention (default 30 days):**
```bash
kubectl patch deployment prometheus -n mlflow-prod -p \
  '{"spec":{"template":{"spec":{"containers":[{"name":"prometheus","args":["--storage.tsdb.retention.time=365d"]}]}}}}'
```

**Reduce cardinality (high memory usage):**
Edit `k8s/monitoring/prometheus-config.yaml` and add metric relabeling:
```yaml
metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'node_(network|netdev).*'
    action: drop  # Drop high-cardinality metrics
```

**Increase Prometheus resources:**
```yaml
resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 2Gi
```

<h3>8.9) Troubleshooting</h3>

**Prometheus targets not scraping:**
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

## 🖥️ Streamlit Application for Local Prediction

This project includes an interactive user interface built with **Streamlit** to perform predictions locally in a user-friendly way. Ideal for demonstrations and quick model testing.

### Quick Start (Local)

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

### Features

-   **User-Friendly Interface:** Inputs for the 30 model features.
-   **Real-time Predictions:** Submit values to get the prediction (benign/malignant) and probabilities.
-   **Random Feature Generation:** Button to populate fields with random values for quick testing.
-   **Dynamic Loading:** Loads the model and its metadata (`metadata.json`) dynamically, ensuring the interface reflects the trained model.

---

## ✅ Best Practices
- Modular and scalable structure
- Clean versioning with `.gitignore`
- Complete experiment tracking with MLflow
- Clear separation of **ETL, training, evaluation, and deployment**
- Technical documentation tailored for recruiters
- **Clean Code & Consistency:** Code refactored for greater clarity, less hardcoding, and dynamic model metadata loading.
- **Dynamic Model Metadata:** FastAPI and Streamlit now dynamically load model metadata (`metadata.json`) and feature names, reducing the chance of inconsistencies.

---

<h2> 🔮 Future Extensions</h2>
- Integration with **Docker/Kubernetes**
- Pipeline automation with **CI/CD (GitHub Actions)**
- Model monitoring in production
- Unit testing and continuous integration
- **MLflow Model Registry:** Integrate model version and stage management via MLflow Model Registry for full lifecycle tracking.
- **Data Drift Monitoring:** Add components to monitor data drift in production and alert on potential performance degradations.