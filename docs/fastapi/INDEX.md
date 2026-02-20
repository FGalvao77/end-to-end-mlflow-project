# 📑 FastAPI API - Quick Reference Index

## 🎯 Quick Links

### Get Started in 5 Minutes
- **Option 1**: [Docker Compose (Easiest)](README.md#quick-start-5-minutes)
- **Option 2**: [Local Development](README.md#quick-start-5-minutes)
- **Option 3**: [Kubernetes](README.md#quick-start-5-minutes)

### Common Tasks
| Task | Command |
|------|---------|
| **Start API** | `docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d api` |
| **Stop API** | `docker compose down` |
| **View logs** | `docker logs -f <container_id>` |
| **Test health** | `curl -s http://127.0.0.1:8000/health \| jq .` |
| **Swagger UI** | `http://127.0.0.1:8000/docs` |
| **Metrics** | `curl -s http://127.0.0.1:8000/metrics` |

---

## 📚 Documentation Map

### For Different Roles

**👨‍💻 Developers**
1. Read: [Architecture Overview](README.md#-architecture-overview)
2. Check: [ENDPOINTS.md](ENDPOINTS.md) - All available routes
3. Reference: [CHEATSHEET.md](CHEATSHEET.md) - Code examples
4. Study: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Design details

**🏗️ DevOps/Infrastructure**
1. Deploy: [Kubernetes Deployment](README.md#-kubernetes-deployment)
2. Monitor: [Monitoring Integration](README.md#-monitoring-integration)
3. Debug: [Troubleshooting](README.md#-troubleshooting)
4. Configure: [Configuration](README.md#-configuration)

**🧪 QA/Testing**
1. Quick start: [Quick Start](README.md#-quick-start-5-minutes)
2. Examples: [Testing Examples](README.md#-testing-examples)
3. Endpoints: [ENDPOINTS.md](ENDPOINTS.md)
4. Cheatsheet: [CHEATSHEET.md](CHEATSHEET.md)

**📊 Data Science/ML**
1. Architecture: [Architecture Overview](README.md#-architecture-overview)
2. Model info: [Configuration](README.md#-configuration)
3. Predictions: [ENDPOINTS.md](ENDPOINTS.md#predictions)
4. Metrics: [Monitoring Integration](README.md#-monitoring-integration)

---

## 🚀 Most Common Commands

### Start/Stop

```bash
# Start entire stack (MLflow + API)
docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d

# Start only API
docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d api

# Stop all
docker compose down

# Rebuild image
docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d --build
```

### Testing

```bash
# Health check
curl -s http://127.0.0.1:8000/health | jq .

# Get model metadata
curl -s http://127.0.0.1:8000/model/metadata | jq .

# Make a prediction
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{...}' | jq .

# View metrics
curl -s http://127.0.0.1:8000/metrics

# Interactive testing
open http://127.0.0.1:8000/docs  # Swagger UI
```

### Docker Debugging

```bash
# View logs (real-time)
docker logs -f <container_id>

# View logs (last 50 lines)
docker logs --tail=50 <container_id>

# Execute command in container
docker exec <container_id> curl http://localhost:8000/health

# Inspect container
docker inspect <container_id>
```

### Kubernetes

```bash
# Deploy
kubectl apply -f k8s/fastapi-deployment.yaml

# Check status
kubectl get all -n mlflow-prod | grep fastapi

# View logs
kubectl logs deployment/fastapi-api -n mlflow-prod -f

# Port-forward
kubectl port-forward svc/fastapi-service -n mlflow-prod 8000:8000

# Scale manually
kubectl scale deployment fastapi-api --replicas=5 -n mlflow-prod

# Delete
kubectl delete -f k8s/fastapi-deployment.yaml
```

---

## 📋 Key Endpoints Reference

### Health & Status
```
GET  http://127.0.0.1:8000/health          ← Kubernetes liveness probe
GET  http://127.0.0.1:8000/ping            ← MLflow compatibility check
```

### Model Info
```
GET  http://127.0.0.1:8000/model/metadata  ← Accuracy, F1, classes
GET  http://127.0.0.1:8000/model/features  ← Expected feature names
```

### Predictions
```
POST http://127.0.0.1:8000/predict         ← Single prediction (30 features)
POST http://127.0.0.1:8000/batch-predict   ← Batch predictions (1-1000)
POST http://127.0.0.1:8000/invocations     ← MLflow-compatible format
```

### Monitoring
```
GET  http://127.0.0.1:8000/metrics         ← Prometheus metrics
GET  http://127.0.0.1:8000/prometheus-metrics  ← Explicit format
GET  http://127.0.0.1:8000/docs            ← Swagger UI (interactive)
GET  http://127.0.0.1:8000/redoc           ← ReDoc (alternative)
```

---

## 🔍 Endpoint Details Reference

See [ENDPOINTS.md](ENDPOINTS.md) for:
- ✅ Full request/response examples
- ✅ Error codes and descriptions
- ✅ Parameter descriptions
- ✅ Status codes
- ✅ Performance notes

---

## 💡 Code Examples

### Python (using requests)
```python
import requests

# Single prediction
response = requests.post(
    'http://127.0.0.1:8000/predict',
    json={'feature_1': 0.5, ..., 'feature_30': 0.3}
)
print(response.json())  # {'prediction': 1, 'probability': [...], 'confidence': 0.92}

# Batch predictions
response = requests.post(
    'http://127.0.0.1:8000/batch-predict',
    json={'records': [{...}, {...}]}
)
print(response.json())  # {'predictions': [...], 'processing_time_ms': 45.23}

# Get metrics
response = requests.get('http://127.0.0.1:8000/metrics')
print(response.text)   # Prometheus metrics
```

### JavaScript/Node.js
```javascript
// Single prediction
const response = await fetch('http://127.0.0.1:8000/predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({feature_1: 0.5, ..., feature_30: 0.3})
});
const result = await response.json();

// Health check
const health = await fetch('http://127.0.0.1:8000/health');
const status = await health.json();
```

### cURL
```bash
# Health check
curl -X GET http://127.0.0.1:8000/health

# Prediction
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"feature_1": 0.5, ...}'

# Batch
curl -X POST http://127.0.0.1:8000/batch-predict \
  -H "Content-Type: application/json" \
  -d '{"records": [{...}, {...}]}'

# Metrics
curl -X GET http://127.0.0.1:8000/metrics
```

---

## ⚙️ Configuration Reference

| Variable | Default | Purpose |
|----------|---------|---------|
| `SERVE_API` | `false` | Enable FastAPI mode |
| `API_PORT` | `8000` | Port to listen on |
| `MODEL_PATH` | `artifacts/model/model.joblib` | Model file location |
| `LOG_LEVEL` | `INFO` | Logging level |
| `PYTHONUNBUFFERED` | `1` | Real-time log output |

---

## 🐳 Docker Information

### Image Details
- **Base**: `python:3.12-slim`
- **Entrypoint**: `docker-entrypoint.sh` (smart 3-mode)
- **Default Mode**: Detects `SERVE_API=true` and starts FastAPI
- **Port**: 8000
- **Health Check**: `/health` endpoint

### Build Command
```bash
docker build -t my-mlflow-app:latest -f src/mlops_project/Dockerfile .
```

### Run Command
```bash
docker run --rm -p 8000:8000 \
  -e SERVE_API=true \
  -v "$(pwd)/artifacts:/artifacts:ro" \
  my-mlflow-app:latest
```

---

## ☸️ Kubernetes Highlights

### Features
- ✅ **Auto-scaling**: 2-5 replicas (CPU/memory based)
- ✅ **Health checks**: Liveness & readiness probes
- ✅ **Service**: NodePort 30800 (external)
- ✅ **Pod disruption budget**: Min 1 available
- ✅ **Network policy**: Security
- ✅ **Resource limits**: CPU 500m, Memory 512Mi

### Namespace
- Default: `mlflow-prod`
- ServiceAccount: `fastapi-api`
- Labels: `app=fastapi-api`

### Files
- Deployment config: [k8s/fastapi-deployment.yaml](../k8s/fastapi-deployment.yaml)
- Full K8s guide: [k8s/README.md](../k8s/README.md)

---

## 📊 Prometheus Metrics

### Available Metrics
```
# Counters
prediction_requests_total{endpoint="..."}       ← Total requests by endpoint
prediction_requests_successful{...}             ← Successful requests
prediction_requests_failed{...}                 ← Failed requests

# Histograms
prediction_latency_seconds{endpoint="...",le="..."} ← Request latency buckets
batch_size_requests{...}                        ← Batch request sizes

# Gauges
model_loaded                                    ← 1 = loaded, 0 = not loaded
api_uptime_seconds                              ← API uptime
```

### Sample PromQL Queries
```promql
sum(rate(prediction_requests_total[5m])) by (endpoint)
histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m]))
(sum(rate(prediction_requests_failed[5m])) / sum(rate(prediction_requests_total[5m]))) * 100
```

---

## 🔗 Important Links

### Documentation
- **Main project**: [../../README.md](../../README.md)
- **Monitoring**: [../monitoring/README.md](../monitoring/README.md)
- **Kubernetes**: [../k8s/README.md](../k8s/README.md)
- **Step-by-step**: [../../notebooks/step-by-step_instructions_for_execution.ipynb](../../notebooks/step-by-step_instructions_for_execution.ipynb)

### Source Code
- **FastAPI app**: [src/mlops_project/api.py](../src/mlops_project/api.py) (730+ lines)
- **Pydantic models**: [src/mlops_project/schemas.py](../src/mlops_project/schemas.py) (320+ lines)
- **Docker entrypoint**: [src/mlops_project/docker-entrypoint.sh](../src/mlops_project/docker-entrypoint.sh)
- **Docker compose**: [src/mlops_project/docker-compose.mlflow.yml](../src/mlops_project/docker-compose.mlflow.yml)

---

## 🆘 Need Help?

1. **Not working?** → Check [Troubleshooting](README.md#-troubleshooting)
2. **Command reference?** → See [CHEATSHEET.md](CHEATSHEET.md)
3. **Detailed endpoints?** → Read [ENDPOINTS.md](ENDPOINTS.md)
4. **Architecture?** → Study [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
5. **Still stuck?** → Check logs with `docker logs` or `kubectl logs`

---

**Total Lines of FastAPI Code**: 1,050+ lines (api.py + schemas.py)  
**Supported Endpoints**: 13 endpoints  
**Response Format**: JSON  
**Authentication**: None (add as needed)  
**Status**: ✅ Production Ready
