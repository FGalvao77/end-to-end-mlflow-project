# 🎯 FastAPI API - Cheatsheet

Quick reference for common operations and code examples.

---

## 🚀 Quick Start Commands

### Docker Compose
```bash
# Start entire stack
export DOCKER_API_VERSION=1.44
docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d

# Start only API
docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d api

# View logs
docker compose logs -f api

# Stop all
docker compose down

# Restart
docker compose restart api

# Rebuild image
docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d --build
```

### Local Development
```bash
# Activate venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start with auto-reload
python -m uvicorn src.mlops_project.api:app --reload

# Start with specific port
python -m uvicorn src.mlops_project.api:app --port 8001 --reload

# Production mode (no auto-reload)
python -m uvicorn src.mlops_project.api:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🧪 Testing Endpoints

### Health Check
```bash
# Simple health check
curl -s http://127.0.0.1:8000/health | jq .

# With verbose output
curl -v http://127.0.0.1:8000/health

# Check response code only
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/health
```

### Get Model Info
```bash
# Model metadata
curl -s http://127.0.0.1:8000/model/metadata | jq .

# Feature names
curl -s http://127.0.0.1:8000/model/features | jq '.features | .[:5]'  # First 5 features
```

### Single Prediction (Minimal Example)
```bash
# Create a temporary request file
cat > /tmp/pred.json << 'EOF'
{
  "feature_1": 13.54, "feature_2": 14.36, "feature_3": 87.46,
  "feature_4": 566.3, "feature_5": 0.09779, "feature_6": 0.08129,
  "feature_7": 0.06664, "feature_8": 0.04781, "feature_9": 0.1879,
  "feature_10": 0.05766, "feature_11": 0.2699, "feature_12": 0.7886,
  "feature_13": 2.058, "feature_14": 23.56, "feature_15": 0.008462,
  "feature_16": 0.0146, "feature_17": 0.02387, "feature_18": 0.01315,
  "feature_19": 0.0145, "feature_20": 0.004949, "feature_21": 15.47,
  "feature_22": 23.75, "feature_23": 103.4, "feature_24": 741.6,
  "feature_25": 0.1791, "feature_26": 0.5249, "feature_27": 0.5355,
  "feature_28": 0.175, "feature_29": 0.6565, "feature_30": 0.1193
}
EOF

# Make prediction
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d @/tmp/pred.json | jq .
```

### Batch Predictions
```bash
# Make batch prediction
curl -X POST http://127.0.0.1:8000/batch-predict \
  -H "Content-Type: application/json" \
  -d '{
    "records": [
      {"feature_1": 13.54, "feature_2": 14.36, ..., "feature_30": 0.1193},
      {"feature_1": 9.504, "feature_2": 12.44, ..., "feature_30": 0.1404}
    ]
  }' | jq .
```

### Prometheus Metrics
```bash
# View all metrics
curl -s http://127.0.0.1:8000/metrics | head -50

# Filter prediction metrics
curl -s http://127.0.0.1:8000/metrics | grep prediction_requests_total

# Filter latency metrics
curl -s http://127.0.0.1:8000/metrics | grep prediction_latency

# Count total requests
curl -s http://127.0.0.1:8000/metrics | grep "^prediction_requests_total" | wc -l
```

---

## 🐍 Python Code Examples

### Basic Setup
```python
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.status_code)  # 200
print(response.json())       # {'status': 'healthy', ...}
```

### Single Prediction
```python
# Create sample data (30 features)
sample_data = {f"feature_{i}": 0.5 for i in range(1, 31)}

# Make prediction
response = requests.post(
    f"{BASE_URL}/predict",
    json=sample_data
)

if response.status_code == 200:
    result = response.json()
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']:.2%}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

### Batch Predictions
```python
# Create batch data (multiple samples)
batch_records = [
    {f"feature_{i}": 0.5 for i in range(1, 31)},
    {f"feature_{i}": 0.3 for i in range(1, 31)},
    {f"feature_{i}": 0.7 for i in range(1, 31)},
]

# Make batch prediction
response = requests.post(
    f"{BASE_URL}/batch-predict",
    json={"records": batch_records}
)

result = response.json()
print(f"Total records: {result['total_records']}")
print(f"Processing time: {result['processing_time_ms']:.2f}ms")

for i, pred in enumerate(result['predictions']):
    print(f"Sample {i}: {pred['prediction']} (confidence: {pred['confidence']:.2%})")
```

### Get Model Info
```python
# Get metadata
response = requests.get(f"{BASE_URL}/model/metadata")
metadata = response.json()
print(f"Model: {metadata['name']}")
print(f"Accuracy: {metadata['accuracy']:.2%}")
print(f"F1-Score: {metadata['f1_score']:.2%}")

# Get features
response = requests.get(f"{BASE_URL}/model/features")
features = response.json()['features']
print(f"Number of features: {len(features)}")
print(f"First 5 features: {features[:5]}")
```

### Error Handling
```python
try:
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"feature_1": 0.5}  # Missing 29 features!
    )
    response.raise_for_status()  # Raise exception for bad status
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}")
    print(f"Message: {e.response.json()}")
except requests.exceptions.ConnectionError:
    print("Connection failed - is the API running?")
```

### Monitoring & Performance
```python
import time

# Load test - make multiple predictions and time them
times = []
for i in range(100):
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/predict",
        json={f"feature_{j}": 0.5 for j in range(1, 31)}
    )
    elapsed = time.time() - start
    times.append(elapsed)

print(f"Average latency: {sum(times)/len(times)*1000:.2f}ms")
print(f"Min latency: {min(times)*1000:.2f}ms")
print(f"Max latency: {max(times)*1000:.2f}ms")

# Get API metrics
response = requests.get(f"{BASE_URL}/metrics")
for line in response.text.split('\n'):
    if 'prediction_requests_total' in line and not line.startswith('#'):
        print(line)
```

---

## 🐳 Docker Commands

### Build & Run
```bash
# Build image
docker build -t my-mlflow-app:latest -f src/mlops_project/Dockerfile .

# Run image
docker run --rm -p 8000:8000 \
  -e SERVE_API=true \
  -v "$(pwd)/artifacts:/artifacts:ro" \
  my-mlflow-app:latest

# Run with environment variables
docker run --rm -p 8000:8000 \
  -e SERVE_API=true \
  -e LOG_LEVEL=DEBUG \
  -e API_PORT=8000 \
  -v "$(pwd)/artifacts:/artifacts:ro" \
  my-mlflow-app:latest

# Run with custom model path
docker run --rm -p 8000:8000 \
  -e SERVE_API=true \
  -e MODEL_PATH=/custom/model.joblib \
  -v "$(pwd)/my-model:/custom:ro" \
  my-mlflow-app:latest
```

### Container Inspection
```bash
# List running containers
docker ps

# View logs
docker logs <container_id>
docker logs -f <container_id>  # Follow logs
docker logs --tail=50 <container_id>  # Last 50 lines

# Execute command
docker exec <container_id> curl http://localhost:8000/health

# Inspect container
docker inspect <container_id>

# Container stats
docker stats <container_id>
```

### Docker Compose
```bash
# View service status
docker compose -f src/mlops_project/docker-compose.mlflow.yml ps

# View one service
docker compose -f src/mlops_project/docker-compose.mlflow.yml ps api

# View environment
docker compose -f src/mlops_project/docker-compose.mlflow.yml config | grep -A 5 "api:"

# Clean up (remove containers, volumes)
docker compose -f src/mlops_project/docker-compose.mlflow.yml down -v
```

---

## ☸️ Kubernetes Commands

### Deployment
```bash
# Deploy
kubectl apply -f k8s/fastapi-deployment.yaml

# Check deployment status
kubectl get deployment fastapi-api -n mlflow-prod
kubectl describe deployment fastapi-api -n mlflow-prod

# Check pods
kubectl get pods -n mlflow-prod -l app=fastapi-api
kubectl get pods -n mlflow-prod -l app=fastapi-api -o wide

# View pod details
kubectl describe pod <pod_name> -n mlflow-prod
```

### Logs & Debugging
```bash
# View logs (current)
kubectl logs deployment/fastapi-api -n mlflow-prod

# Follow logs
kubectl logs deployment/fastapi-api -n mlflow-prod -f

# View logs from all pods
kubectl logs -l app=fastapi-api -n mlflow-prod

# View logs with timestamps
kubectl logs deployment/fastapi-api -n mlflow-prod --timestamps=true

# View previous logs (if pod crashed)
kubectl logs deployment/fastapi-api -n mlflow-prod --previous

# Tail logs
kubectl logs deployment/fastapi-api -n mlflow-prod --tail=100
```

### Port Forwarding & Testing
```bash
# Port-forward to local
kubectl port-forward svc/fastapi-service -n mlflow-prod 8000:8000

# In another terminal, test:
curl -s http://localhost:8000/health | jq .

# Port-forward with background
kubectl port-forward svc/fastapi-service -n mlflow-prod 8000:8000 &
sleep 2
curl -s http://localhost:8000/health
fg  # Return to foreground to stop
```

### Scaling & Management
```bash
# Scale deployment
kubectl scale deployment fastapi-api --replicas=5 -n mlflow-prod

# Check auto-scaler status
kubectl get hpa -n mlflow-prod

# Manual rolling restart
kubectl rollout restart deployment/fastapi-api -n mlflow-prod

# Check rollout status
kubectl rollout status deployment/fastapi-api -n mlflow-prod

# Rollback to previous version
kubectl rollout undo deployment/fastapi-api -n mlflow-prod
```

### Resource Inspection
```bash
# View resource usage
kubectl top nodes
kubectl top pods -n mlflow-prod

# Get pod info (wide format)
kubectl get pods -n mlflow-prod -o wide

# Get resource definitions
kubectl get deployment fastapi-api -n mlflow-prod -o yaml

# Edit deployment
kubectl edit deployment fastapi-api -n mlflow-prod
```

---

## 🔍 Monitoring & Metrics

### Prometheus Port-Forward
```bash
# Start port-forward
kubectl port-forward svc/prometheus -n mlflow-prod 9090:9090 &

# In browser or with curl:
curl -s http://localhost:9090/api/v1/targets | jq .

# Query metrics
curl -s 'http://localhost:9090/api/v1/query?query=up' | jq .

# Stop port-forward
jobs
fg
ctrl+c
```

### Grafana Access
```bash
# Start port-forward
kubectl port-forward svc/grafana -n mlflow-prod 3000:3000 &

# Access: http://localhost:3000
# Default login: admin / admin123456789

# Stop when done
kill %1
```

### PromQL Queries
```promql
# Request rate (per second)
sum(rate(prediction_requests_total[5m])) by (endpoint)

# Error rate (percentage)
(sum(rate(prediction_requests_failed[5m])) / sum(rate(prediction_requests_total[5m]))) * 100

# Latency percentiles
histogram_quantile(0.50, rate(prediction_latency_seconds_bucket[5m]))  # p50
histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m]))  # p95
histogram_quantile(0.99, rate(prediction_latency_seconds_bucket[5m]))  # p99

# Model status
model_loaded

# API uptime
api_uptime_seconds
```

---

## 🧹 Cleanup & Reset

### Docker
```bash
# Stop all containers
docker stop $(docker ps -q)

# Remove all containers
docker rm $(docker ps -aq)

# Remove image
docker rmi my-mlflow-app:latest

# Prune everything (careful!)
docker system prune -a --volumes
```

### Kubernetes
```bash
# Delete deployment
kubectl delete -f k8s/fastapi-deployment.yaml

# Delete namespace (removes all resources in it)
kubectl delete namespace mlflow-prod

# Delete specific resource
kubectl delete deployment fastapi-api -n mlflow-prod

# Delete service
kubectl delete service fastapi-service -n mlflow-prod
```

### Local Development
```bash
# Remove virtual environment
rm -rf .venv

# Reinstall dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name '*.pyc' -delete
```

---

## 📝 Useful Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
# API testing
alias api-health='curl -s http://127.0.0.1:8000/health | jq .'
alias api-metadata='curl -s http://127.0.0.1:8000/model/metadata | jq .'
alias api-metrics='curl -s http://127.0.0.1:8000/metrics'

# Docker
alias dc='docker compose -f src/mlops_project/docker-compose.mlflow.yml'
alias dc-up='docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d'
alias dc-down='docker compose -f src/mlops_project/docker-compose.mlflow.yml down'
alias dc-logs='docker compose -f src/mlops_project/docker-compose.mlflow.yml logs -f'

# Kubernetes
alias k='kubectl'
alias kn='kubectl -n mlflow-prod'
alias klog='kubectl logs deployment/fastapi-api -n mlflow-prod -f'
alias kpf='kubectl port-forward svc/fastapi-service -n mlflow-prod 8000:8000'
```

Usage:
```bash
api-health
dc up
klog
```

---

## 🔗 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

---

**Last Updated**: 2024  
**Status**: ✅ Production Ready
