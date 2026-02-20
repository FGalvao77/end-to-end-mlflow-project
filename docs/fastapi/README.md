# 🚀 FastAPI Model Serving API Documentation

This directory contains documentation and configuration for the **FastAPI REST API** serving machine learning model predictions. The API is production-ready with integrated monitoring, validation, and Kubernetes support.

---

## 📖 Quick Navigation

| Document | Purpose |
|----------|---------|
| [INDEX.md](INDEX.md) | Complete guide index and quick reference |
| [CHEATSHEET.md](CHEATSHEET.md) | Common commands and code snippets |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Implementation details and architecture |
| [ENDPOINTS.md](ENDPOINTS.md) | Detailed endpoint reference guide |

---

## 🎯 Quick Start (5 minutes)

### Option 1: Docker Compose (Easiest)

```bash
# Start API with MLflow backend
export DOCKER_API_VERSION=1.44
docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d api

# Test the API
curl -s http://127.0.0.1:8000/health | jq .

# View Swagger UI
# Open http://127.0.0.1:8000/docs in your browser
```

### Option 2: Local Development

```bash
# Activate virtual environment
source .venv/bin/activate

# Start API server with auto-reload
python -m uvicorn src.mlops_project.api:app --reload

# The API will be available at:
# - API: http://127.0.0.1:8000
# - Swagger UI: http://127.0.0.1:8000/docs
# - ReDoc: http://127.0.0.1:8000/redoc
```

### Option 3: Kubernetes

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/fastapi-deployment.yaml

# Port-forward for local testing
kubectl port-forward svc/fastapi-service -n mlflow-prod 8000:8000

# Test
curl -s http://localhost:8000/health | jq .
```

---

## 📚 Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              FastAPI Application                    │
├─────────────────────────────────────────────────────┤
│  Routes:                                            │
│  ├─ /health, /ping           → Health checks       │
│  ├─ /model/*                 → Model information   │
│  ├─ /predict                 → Single prediction   │
│  ├─ /batch-predict           → Batch predictions   │
│  ├─ /invocations             → MLflow compatible   │
│  └─ /metrics                 → Prometheus metrics  │
├─────────────────────────────────────────────────────┤
│  Components:                                        │
│  ├─ Pydantic Models (schemas.py)                   │
│  ├─ Prometheus Metrics Middleware                  │
│  ├─ Auto Model Loading (Lifespan)                  │
│  └─ Error Handling & Validation                    │
└─────────────────────────────────────────────────────┘
```

---

## 🔌 API Endpoints Summary

### Health & Status
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Liveness probe (Kubernetes compatible) |
| GET | `/ping` | Readiness check (MLflow compatible) |

### Model Information
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/model/metadata` | Model info (accuracy, F1, classes) |
| GET | `/model/features` | Expected feature names |

### Predictions
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/predict` | Single prediction (30 features) |
| POST | `/batch-predict` | Batch predictions (1-1000 items) |
| POST | `/invocations` | MLflow-compatible format |

### Monitoring
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/metrics` | Prometheus metrics |
| GET | `/prometheus-metrics` | Explicit Prometheus format |
| GET | `/docs` | Swagger UI documentation |
| GET | `/redoc` | ReDoc documentation |

---

## 🧪 Testing Examples

### 1. Health Check
```bash
curl -X GET http://127.0.0.1:8000/health | jq .
```

### 2. Make a Prediction
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "feature_1": 0.5, "feature_2": 0.3, "feature_3": 0.7,
    ... (30 features total)
  }' | jq .
```

### 3. Batch Predictions
```bash
curl -X POST http://127.0.0.1:8000/batch-predict \
  -H "Content-Type: application/json" \
  -d '{
    "records": [
      {"feature_1": 0.5, ..., "feature_30": 0.3},
      {"feature_1": 0.2, ..., "feature_30": 0.8}
    ]
  }' | jq .
```

### 4. View Metrics
```bash
curl -s http://127.0.0.1:8000/metrics | grep prediction_requests_total
```

---

## 🐳 Docker & Docker Compose

### Build Docker Image
```bash
export DOCKER_API_VERSION=1.44
docker build -t my-mlflow-app:latest -f src/mlops_project/Dockerfile .
```

### Run with Docker Compose
```bash
# Start all services
docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d

# Start only API
docker compose -f src/mlops_project/docker-compose.mlflow.yml up -d api

# View logs
docker compose logs -f api

# Stop all
docker compose down
```

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `SERVE_API` | false | Enable FastAPI mode |
| `API_PORT` | 8000 | Port to listen on |
| `MODEL_PATH` | `artifacts/model/model.joblib` | Path to trained model |
| `LOG_LEVEL` | INFO | Logging level (DEBUG/INFO/WARNING/ERROR) |

---

## ☸️ Kubernetes Deployment

### Deploy to Kubernetes
```bash
# Deploy all FastAPI resources
kubectl apply -f k8s/fastapi-deployment.yaml

# Verify
kubectl get all -n mlflow-prod | grep fastapi

# Port-forward for local testing
kubectl port-forward svc/fastapi-service -n mlflow-prod 8000:8000
```

### Kubernetes Features
- ✅ **Auto-scaling**: 2-5 replicas based on CPU
- ✅ **Health checks**: Liveness and readiness probes
- ✅ **Pod disruption budgets**: Maintains minimum availability
- ✅ **Network policies**: Secure traffic control
- ✅ **Resource limits**: CPU/memory requests and limits

### View Pod Status
```bash
# Get FastAPI pods
kubectl get pods -n mlflow-prod -l app=fastapi-api

# View pod logs
kubectl logs deployment/fastapi-api -n mlflow-prod --tail=50 -f

# Describe pod for debugging
kubectl describe pod <pod_name> -n mlflow-prod
```

---

## 📊 Monitoring Integration

The API exports Prometheus-compatible metrics at `/metrics`:

### Key Metrics
```promql
# Prediction request rate
sum(rate(prediction_requests_total[5m])) by (endpoint)

# Error rate
sum(rate(prediction_requests_failed[5m])) by (endpoint)

# Latency (p95)
histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m]))

# Model load status
model_loaded

# API uptime
api_uptime_seconds
```

### View in Grafana
```bash
# Port-forward Grafana
kubectl port-forward svc/grafana -n mlflow-prod 3000:3000

# Access: http://127.0.0.1:3000 (admin/admin123456789)
# Dashboard: "MLflow & Model Server Monitoring"
```

---

## 🔧 Configuration

### Model Requirements
- **Format**: scikit-learn model (joblib-serialized)
- **Input**: Exactly 30 numeric features
- **Output**: Supports `.predict()` and `.predict_proba()`
- **Location**: `artifacts/model/model.joblib`

### Pydantic Validation
All API requests are validated using Pydantic models defined in `src/mlops_project/schemas.py`:
- `PredictionRequest`: Single prediction input
- `PredictionResponse`: Single prediction output
- `BatchPredictionRequest/Response`: Batch operations
- `HealthResponse`: Health status
- `ErrorResponse`: Error details

---

## 🐛 Troubleshooting

### API not starting
```bash
# Check logs
docker logs <container_id>
kubectl logs deployment/fastapi-api -n mlflow-prod

# Verify model file exists
ls -la artifacts/model/model.joblib

# Check port is available
netstat -tln | grep 8000
```

### Model not loading
```bash
# Verify path is correct
echo $MODEL_PATH
ls -la $MODEL_PATH

# Check permissions
stat artifacts/model/

# Train model if missing
python -m src.mlops_project.train
```

### Kubernetes pod crashing
```bash
# Check pod status
kubectl describe pod <pod_name> -n mlflow-prod

# View logs with timestamps
kubectl logs pod/<pod_name> -n mlflow-prod --timestamps=true

# Check resource limits
kubectl top nodes
kubectl top pods -n mlflow-prod
```

---

## 📁 File Structure

```
fastapi-api/
├── README.md                          # This file
├── INDEX.md                           # Quick reference guide
├── CHEATSHEET.md                      # Common commands
├── ENDPOINTS.md                       # Detailed endpoint docs
└── IMPLEMENTATION_SUMMARY.md          # Architecture & design details

Core Implementation:
src/mlops_project/
├── api.py                             # FastAPI application (730+ lines)
├── schemas.py                         # Pydantic models (320+ lines)
├── docker-entrypoint.sh               # Smart entrypoint (3-mode)
└── docker-compose.mlflow.yml          # Docker Compose with API service

Kubernetes:
k8s/
└── fastapi-deployment.yaml            # Complete K8s manifest
```

---

## 📖 Learning Path

1. **Start here**: Read [INDEX.md](INDEX.md) for quick reference
2. **Quick commands**: See [CHEATSHEET.md](CHEATSHEET.md) for common operations
3. **Deep dive**: Study [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
4. **Endpoint details**: Reference [ENDPOINTS.md](ENDPOINTS.md) for all routes
5. **Hands-on**: Try the examples in quick start above

---

## 🔗 Related Documentation

- **Main README**: [../../README.md](../../README.md)
- **Monitoring Guide**: [../monitoring/README.md](../monitoring/README.md)
- **Kubernetes Guide**: [../k8s/README.md](../k8s/README.md)
- **Step-by-step Guide**: [../../notebooks/step-by-step_instructions_for_execution.ipynb](../../notebooks/step-by-step_instructions_for_execution.ipynb)

---

## 🚀 Next Steps

✅ **What's working:**
- Fast REST API for single and batch predictions
- Kubernetes-ready deployment
- Prometheus metrics integration
- Swagger UI for interactive testing

📋 **Potential enhancements:**
- Add request/response caching
- Implement rate limiting
- Add API authentication (JWT/OAuth2)
- Database logging for predictions
- Advanced model versioning
- A/B testing endpoints
- Async prediction processing

---

## 📝 Notes

- All endpoints are documented in Swagger UI at `/docs`
- Model is automatically loaded at API startup (fail-fast)
- Prometheus metrics are collected for all operations
- Kubernetes manifests include auto-scaling and failover
- Health checks are compatible with both Docker and K8s

---

**Last Updated**: 2024  
**Version**: 1.0.0  
**Status**: Production Ready ✅
