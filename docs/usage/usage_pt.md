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
http://172.0.0.1:8000/docs
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

<h2> ⚙️ System Prerequisites</h2>

### Kubernetes & Minikube (required for deployment)

**⚠️ IMPORTANT:** Before running any `kubectl` commands or interacting with Kubernetes, you **must have Minikube installed and an active Kubernetes cluster**. Minikube is the simplest and recommended way for local development.

<h4>Minikube Installation</h4>

**Linux:**
```bash
# Download the Minikube binary
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
# Make it executable and move it to a location in your PATH
sudo install minikube-linux-amd64 /usr/local/bin/minikube
# Remove the downloaded file (optional)
rm minikube-linux-amd64
```

**macOS:**
```bash
brew install minikube
```

**Windows:**
```bash
choco install minikube
# or manual download: https://github.com/kubernetes/minikube/releases
```
**After installation, ensure Minikube is in your PATH and configured to use your preferred driver (docker, virtualbox, etc.).**

<h4>Starting Minikube</h4>

```bash
# Start the cluster (may take a few minutes on first run)
minikube start --driver=docker # Or use your preferred driver, e.g., virtualbox, podman

# Check status - MUST show 'host: Running, kubelet: Running, apiserver: Running'
minikube status

# Confirm Kubernetes connectivity - MUST list your nodes
kubectl cluster-info
kubectl get nodes
```

When all statuses are `Running` or return information, your Kubernetes environment is ready! ✅

<h4>Stop/Reset Minikube</h4>

```bash
# Stop (preserves data)
minikube stop

# Reset (cleans everything)
minikube delete
minikube start  # starts new cluster
```

---

<h2> 0) Overview of What Already Exists</h2>

- **Training**: `train.py` trains a `RandomForest` inside a `Pipeline` with `StandardScaler`, computes metrics, saves artifacts in `artifacts/model` and (if available) logs to MLflow.  
- **Config**: `configs.yaml` defines `test_size`, `random_state`, hyperparameters and export folder.  
- **Data**: `data_prep.py` uses scikit-learn's `load_breast_cancer` and performs a stratified split.  
- **Util**: `utils.py` loads YAML (the function `load_config`).  
- **Tracking**: `docker-compose.mlflow.yml` brings up a file‑based MLflow Server on port 5000.  
- **Kubernetes**: `deployment.yaml` defines a Deployment/Service for the image `projeto10-model:latest` (port 8000, `/ping`, NodePort 30080).

---

<h2> 1) Prepare Local Environment</h2>

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

<h2> 2) Inspect and Adjust `configs.yaml`</h2>

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

**⚠️ Prerequisite:** Ensure **Minikube is installed and a cluster is running** (see "System Prerequisites" section for instructions).

This project includes a complete monitoring solution using **Prometheus** and **Grafana** for observability of MLflow and model serving infrastructure.

<h3>Quick Start</h3>

**1. Deploy Monitoring Stack:**
    The `scripts/monitoring.sh` automates the deployment of all monitoring components into your Kubernetes cluster.
    ```bash
    # Make the script executable (if not already)
    chmod +x scripts/monitoring.sh

    # Deploy the monitoring stack
    ./scripts/monitoring.sh deploy
    ```
    This command will create a `mlflow-prod` namespace (if it doesn't exist) and apply the Kubernetes manifests for Prometheus and Grafana.

**2. Set up Port-Forwarding for Local Access:**
    To access Prometheus and Grafana from your local browser, you need to port-forward the Kubernetes services to your machine. The `monitoring.sh` script can do this for you:
    ```bash
    ./scripts/monitoring.sh port-forward
    ```
    You will see messages indicating that the ports are being forwarded in the background.

**3. Access Prometheus in Browser:**
    Open your browser and navigate to the following address:
    ```
    http://127.0.0.1:9090
    ```
    You can check the "Targets" page to confirm Prometheus is scraping metrics from your MLflow and model services. To do this, use the command:
    ```bash
    ./scripts/monitoring.sh check-targets
    ```

**4. Access Grafana in Browser:**
    Open another browser tab and go to the following address:
    ```
    http://127.0.0.1:3000
    ```
    You will be prompted to log in. Use the default credentials:
    *   **Username:** `admin`
    *   **Password:** `admin123456789`
    After logging in, navigate to "Dashboards" and select the pre-configured **"MLflow & Model Server Monitoring"** dashboard to visualize your metrics.

<h3>Other Practical Needs</h3>

*   **Check Component Status:**
    ```bash
    ./scripts/monitoring.sh status
    ```
*   **View Logs:**
    ```bash
    ./scripts/monitoring.sh logs prometheus
    ./scripts/monitoring.sh logs grafana
    ```
*   **Clean up Monitoring Stack:**
    ```bash
    ./scripts/monitoring.sh cleanup
    ```
    (Caution: this will remove all deployed monitoring resources)

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
- **Data Drift Monitoring:** Adicionar componentes para monitorar o desvio de dados em produção e alertar sobre potenciais degradações de desempenho.