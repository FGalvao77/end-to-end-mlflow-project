# 🏗️ FastAPI Implementation Summary

Comprehensive technical documentation of the FastAPI API implementation, architecture, and design decisions.

---

## 📖 Table of Contents

1. [Architecture Overview](#-architecture-overview)
2. [Project Structure](#-project-structure)
3. [Technical Stack](#-technical-stack)
4. [Core Components](#-core-components)
5. [API Design](#-api-design)
6. [Data Validation](#-data-validation)
7. [Monitoring & Metrics](#-monitoring--metrics)
8. [Error Handling](#-error-handling)
9. [Performance Optimization](#-performance-optimization)
10. [Deployment](#-deployment)
11. [Security Considerations](#-security-considerations)

---

## 🏗️ Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│              (Python, JavaScript, cURL, etc.)                │
└────┬──────────────────────────────────────────────────────┬─┘
     │                                                        │
     │ HTTP/REST                                             │
     │                                                        │
┌────▼────────────────────────────────────────────────────┬─┴──┐
│             FastAPI Application (api.py)                    │
├─────────────────────────────────────────────────────────────┤
│  Request Pipeline:                                          │
│  1. HTTP Request Received                                  │
│  2. Route Matching (FastAPI Router)                        │
│  3. Pydantic Validation (schemas.py)                       │
│  4. Middleware Processing (CORS, Metrics)                  │
│  5. Request Handling (Endpoint Logic)                      │
│  6. Prometheus Metrics Collection                          │
│  7. Response Serialization & Return                        │
│                                                             │
│  Components:                                                │
│  ├─ Router (13 endpoints)                                 │
│  ├─ Dependency Injection (model loading)                   │
│  ├─ Middleware (CORS, error handling)                      │
│  ├─ Prometheus Integration (metrics)                       │
│  └─ Lifespan Management (startup/shutdown)                 │
└─────────────────────────────────────────────────────────────┘
     │                                                        │
     ├─────────────────────────────────────────────────────┤
     │                                                      │
     │ Model File                  Prometheus Metrics      │
     │                                                      │
     ▼                                                      ▼
┌─────────────────┐                            ┌────────────────┐
│  artifacts/     │                            │  Prometheus    │
│  model/         │                            │  Server        │
│  model.joblib   │                            │  (Optional)    │
└─────────────────┘                            └────────────────┘
     │                                                      │
     │ Loaded at                                           │
     │ Startup                                             │ Scraped
     │ (Fail-fast)                                         │ Every 30s
     │                                                      │
     ▼                                                      ▼
┌─────────────────────────────────────────┐    ┌────────────────┐
│  Scikit-learn Model                      │    │  Grafana       │
│  ├─ .predict() method                   │    │  Dashboards    │
│  └─ .predict_proba() method             │    └────────────────┘
└─────────────────────────────────────────┘
```

### Request Flow Diagram

```
HTTP Input → FastAPI Router → Find Endpoint
                                    ↓
                         ┌──────────────────┐
                         │ Pydantic Validate│
                         │ Request Schema   │
                         └──────────────────┘
                                    ↓
                         ┌──────────────────┐
                         │ Execute Endpoint │
                         │ Logic            │
                         └──────────────────┘
                                    ↓
                         ┌──────────────────┐
                         │ Collect Metrics  │
                         │ (Prometheus)     │
                         └──────────────────┘
                                    ↓
                         ┌──────────────────┐
                         │ Serialize        │
                         │ Response         │
                         └──────────────────┘
                                    ↓
                         HTTP JSON Response
```

---

## 📁 Project Structure

### File Organization

```
end-to-end-mlflow-project/
├── src/mlops_project/
│   ├── api.py                      # Main FastAPI application (730+ lines)
│   │   ├── Global variables
│   │   ├── FastAPI app creation
│   │   ├── Lifespan context manager
│   │   ├── Exception handlers
│   │   ├── Middleware setup
│   │   └── 13 endpoint definitions
│   │
│   ├── schemas.py                  # Pydantic models (320+ lines)
│   │   ├── Request models
│   │   ├── Response models
│   │   ├── Health check models
│   │   ├── Error response models
│   │   └── Validation rules
│   │
│   ├── docker-entrypoint.sh        # Smart container entrypoint
│   │   ├── Environment variable parsing
│   │   ├── 3-mode detection
│   │   └── Service startup logic
│   │
│   ├── docker-compose.mlflow.yml   # Docker Compose with API service
│   │   ├── API service definition
│   │   ├── Health checks
│   │   ├── Volume mounts
│   │   └── Dependencies
│   │
│   └── Dockerfile                  # Container image definition
│       ├── Base: python:3.12-slim
│       ├── Dependencies installation
│       ├── Code copying
│       └── Entrypoint configuration
│
├── k8s/
│   ├── fastapi-deployment.yaml     # Kubernetes manifest (400+ lines)
│   │   ├── Namespace
│   │   ├── ConfigMap
│   │   ├── ServiceAccount
│   │   ├── Deployment
│   │   ├── Service
│   │   ├── HorizontalPodAutoscaler
│   │   ├── PodDisruptionBudget
│   │   ├── NetworkPolicy
│   │   └── ServiceMonitor (optional)
│   │
│   └── README.md                   # Kubernetes guide
│
├── fastapi-api/                    # This documentation
│   ├── README.md                   # Main guide
│   ├── INDEX.md                    # Quick reference
│   ├── CHEATSHEET.md               # Commands & examples
│   └── IMPLEMENTATION_SUMMARY.md   # This file
│
└── artifacts/model/
    ├── model.joblib                # Trained scikit-learn model
    ├── MLmodel                     # MLflow metadata
    ├── conda.yaml                  # Environment
    └── requirements.txt            # Dependencies
```

---

## 🔧 Technical Stack

### Core Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.12+ | Runtime language |
| **FastAPI** | 0.115+ | Web framework (async) |
| **Uvicorn** | 0.30+ | ASGI server |
| **Pydantic** | 2.5+ | Data validation & serialization |
| **scikit-learn** | Latest | ML model |
| **joblib** | Latest | Model serialization |
| **prometheus-client** | 0.20+ | Metrics library |
| **Docker** | Latest | Containerization |
| **Kubernetes** | 1.24+ | Orchestration |

### Dependencies

**Runtime:**
- `fastapi` - High-performance web framework
- `uvicorn[standard]` - ASGI server with WebSocket support
- `pydantic >= 2.5` - Data validation with type hints
- `pydantic-settings >= 2.1` - Settings management
- `prometheus-client >= 0.20` - Prometheus metrics
- `python-multipart >= 0.0.6` - Form data parsing

**Development:**
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatting
- `flake8` - Linting

---

## 🔨 Core Components

### 1. FastAPI Application (`api.py`)

**Purpose**: Main web application handling HTTP requests

**Key Sections:**

#### Imports & Setup
```python
# Core
from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
import joblib
import logging
```

#### Global Prometheus Metrics (730 lines total)
```python
# Counters: Track cumulative events
prediction_requests_total = Counter(
    'prediction_requests_total',
    'Total number of prediction requests',
    ['endpoint']
)

# Histograms: Track distributions
prediction_latency_seconds = Histogram(
    'prediction_latency_seconds',
    'Prediction processing latency',
    ['endpoint'],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0)
)

# Gauges: Track current values
model_loaded = Gauge(
    'model_loaded',
    'Model loading status (1=loaded, 0=not loaded)'
)
```

#### FastAPI App Creation
```python
# Lifespan context manager handles startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load model
    try:
        model = joblib.load(MODEL_PATH)
        model_loaded.set(1)
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        model_loaded.set(0)
    
    yield
    
    # Shutdown: Cleanup (optional)
    logging.info("API shutdown")

app = FastAPI(
    title="MLflow Model Serving API",
    version="1.0.0",
    lifespan=lifespan
)
```

#### 13 Endpoint Definitions

See [Endpoints](#-api-design) section below.

### 2. Pydantic Models (`schemas.py`)

**Purpose**: Request/response validation and serialization

**Key Models (320+ lines):**

```python
class PredictionRequest(BaseModel):
    """Single prediction request"""
    feature_1: float
    feature_2: float
    # ... (30 features total)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"feature_1": 0.5, ..., "feature_30": 0.3}
        }
    )

class PredictionResponse(BaseModel):
    """Single prediction response"""
    prediction: int
    probability: List[float]
    confidence: float
    timestamp: str

class BatchPredictionRequest(BaseModel):
    """Batch prediction request"""
    records: List[PredictionRequest]
    
    @field_validator('records')
    @classmethod
    def validate_batch_size(cls, v):
        if len(v) > 1000:
            raise ValueError('Maximum 1000 records allowed')
        return v

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    model_loaded: bool
    timestamp: str

class ModelMetadata(BaseModel):
    """Model information"""
    name: str
    version: str
    accuracy: float
    f1_score: float
    classes: List[str]
    n_features: int

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    details: str
```

### 3. Docker Integration

#### Entrypoint Script
```bash
#!/bin/bash
# src/mlops_project/docker-entrypoint.sh

# 3-mode detection:
if [ "$SERVE_API" = "true" ]; then
    # FastAPI mode
    python -m uvicorn src.mlops_project.api:app \
        --host 0.0.0.0 --port ${API_PORT:-8000}
elif [ "$SERVE_MODEL" = "true" ]; then
    # MLflow models serve mode
    mlflow models serve -m "$SERVE_MODEL_PATH" -p 8000 --no-conda
else
    # MLflow tracking server mode
    mlflow server --host 0.0.0.0 --port 5000
fi
```

#### Docker Compose Configuration
```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SERVE_API=true
      - MODEL_PATH=/model/model.joblib
      - LOG_LEVEL=INFO
    volumes:
      - ./artifacts/model:/model:ro
      - ./mlruns:/mlruns:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3
    depends_on:
      mlflow:
        condition: service_healthy
```

---

## 🌐 API Design

### Endpoint Categories

#### 1. Health & Status (2 endpoints)
```
GET /health          ← Kubernetes liveness probe
GET /ping            ← MLflow compatibility
```

**Design Decision**: Two separate endpoints for maximum compatibility:
- `/health` for Kubernetes probes (detailed response)
- `/ping` for MLflow model serving compatibility (simple response)

#### 2. Model Information (2 endpoints)
```
GET /model/metadata  ← Model accuracy, F1, classes
GET /model/features  ← Expected feature names
```

**Design Decision**: Separate endpoints for different use cases:
- Metadata for ML tracking
- Features for input validation help

#### 3. Predictions (3 endpoints)
```
POST /predict        ← Single prediction (30 features)
POST /batch-predict  ← Batch predictions (1-1000)
POST /invocations    ← MLflow-compatible format
```

**Design Decision**: 
- `/predict` for simple single predictions
- `/batch-predict` for efficiency (reduce HTTP overhead)
- `/invocations` for MLflow compatibility

**Batch Size Limit**: 1000 records max
- Prevents memory exhaustion
- Ensures reasonable response times
- Large batches split by client

#### 4. Monitoring (3 endpoints)
```
GET /metrics                ← Prometheus format
GET /prometheus-metrics     ← Explicit Prometheus
GET /docs                   ← Swagger UI
GET /redoc                  ← ReDoc docs
```

**Design Decision**: Two metrics endpoints for clarity:
- `/metrics` (default Prometheus format)
- `/prometheus-metrics` (explicit, optional)

---

## 📊 Data Validation

### Input Validation Flow

```
Request JSON
    ↓
Pydantic Model Parsing
    ├─ Type checking (all fields must be float/int)
    ├─ Required fields (all 30 features required for /predict)
    ├─ Range validation (using Field constraints)
    └─ Custom validators (batch size, etc.)
    ↓
Model Fit Check (if model not loaded)
    ↓
Prediction Execution
    ↓
Response Serialization (Pydantic model)
    ↓
JSON Response
```

### Validation Rules

**PredictionRequest:**
- Exactly 30 features required
- All features must be numeric (float/int)
- No NaN or infinity values allowed (implicit via Pydantic)

**BatchPredictionRequest:**
- `records` list with 1-1000 items
- Each item must be valid PredictionRequest
- Non-empty list required

**Example Error:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "feature_15"],
      "msg": "Field required",
      "input": {...}
    }
  ]
}
```

---

## 📈 Monitoring & Metrics

### Prometheus Metrics Exposed

#### Counters (Cumulative)
```
prediction_requests_total{endpoint="predict"}       # Total requests
prediction_requests_successful{endpoint="predict"}  # Success count
prediction_requests_failed{endpoint="predict"}      # Failure count
```

#### Histograms (Distributions)
```
prediction_latency_seconds_bucket{endpoint="predict",le="0.01"}  # < 10ms
prediction_latency_seconds_bucket{endpoint="predict",le="0.1"}   # < 100ms
prediction_latency_seconds_bucket{endpoint="predict",le="1.0"}   # < 1s
```

#### Gauges (Current Values)
```
model_loaded                 # 1 = loaded, 0 = not loaded
api_uptime_seconds          # Seconds since API started
```

### Metric Collection Points

```python
# 1. Request start
start_time = time.time()
request_count += 1
prometheus_counter.inc()

# 2. After validation
validation_time = time.time() - start_time

# 3. After prediction
prediction = model.predict(data)
latency = time.time() - start_time

# 4. Record metrics
prometheus_histogram.observe(latency, labels={...})
prometheus_counter.labels(status='success').inc()

# 5. Return response
return {"prediction": prediction, ...}
```

### Example PromQL Queries

```promql
# Request rate (requests per second)
sum(rate(prediction_requests_total[5m])) by (endpoint)

# Error rate (percentage)
(sum(rate(prediction_requests_failed[5m])) / sum(rate(prediction_requests_total[5m]))) * 100

# Latency percentiles
histogram_quantile(0.95, rate(prediction_latency_seconds_bucket[5m]))

# Requests by status
sum(increase(prediction_requests_total[5m])) by (status)

# Model availability
model_loaded
```

---

## 🚨 Error Handling

### HTTP Status Codes

| Code | Scenario | Example |
|------|----------|---------|
| 200 | Success | Prediction returned |
| 400 | Bad request | Wrong feature count |
| 404 | Not found | Model file missing |
| 500 | Server error | Model prediction failed |

### Error Response Format

All errors follow standard format:
```json
{
  "error": "Error type",
  "details": "Detailed error message",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### Exception Handlers

```python
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Validation error", "details": str(exc)}
    )

@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Model not found", "details": str(exc)}
    )
```

---

## ⚡ Performance Optimization

### 1. Model Loading Strategy

**Approach**: Load at startup (fail-fast)
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load model once at startup
    model = joblib.load(MODEL_PATH)
    # Share across all requests
    yield
    # Cleanup on shutdown
```

**Alternative**: Load on-demand (lazy loading)
- Pro: Faster startup
- Con: First request slower, model reloading overhead

**Chosen**: Startup loading
- Reason: Kubernetes prefers fast startup detection
- Health checks require model availability

### 2. Batch Prediction Optimization

**Size Limits:**
- Single prediction: ~5ms
- Batch 10: ~15ms (5ms + 10ms batch overhead)
- Batch 1000: ~500ms

**Optimization**: Max 1000 per request
- Prevents memory exhaustion
- Keeps latency under 1 second (p95)

### 3. Concurrency

**FastAPI/Uvicorn Features:**
- Async request handling
- Thread pool for blocking I/O
- Multiple worker processes (Kubernetes)

**Deployment**: 4 workers (Kubernetes ReplicaSet)
- Each pod: 1 worker + 1 replica = 2-4 concurrent requests
- Total: 2-5 pods × 4 workers = 8-20 concurrent requests

### 4. Memory Optimization

**Model Storage:** ~50MB (typical scikit-learn model)
**Memory per Request:** ~10MB (batch of 10)
**Container Limit:** 512Mi

**Margin:** ~450MB buffer for:
- Framework overhead
- Request queueing
- Spike handling

---

## ☸️ Deployment

### Docker Deployment

```bash
# Build
docker build -t my-mlflow-app:latest -f src/mlops_project/Dockerfile .

# Run
docker run -p 8000:8000 \
  -e SERVE_API=true \
  -v $(pwd)/artifacts:/artifacts:ro \
  my-mlflow-app:latest
```

### Kubernetes Deployment

**Features:**
- ✅ 2-5 replicas (auto-scaling on CPU)
- ✅ Health checks (liveness + readiness)
- ✅ Resource limits (CPU 500m, Memory 512Mi)
- ✅ Pod anti-affinity (spread across nodes)
- ✅ Pod disruption budget (min 1 available)

**Deployment Steps:**
```bash
kubectl apply -f k8s/fastapi-deployment.yaml
kubectl get all -n mlflow-prod | grep fastapi
kubectl port-forward svc/fastapi-service -n mlflow-prod 8000:8000
```

---

## 🔒 Security Considerations

### Current Implementation

**What's Implemented:**
- ✅ CORS enabled (all origins) - for development
- ✅ Input validation (Pydantic)
- ✅ Error sanitization
- ✅ Read-only model volume mounts

### Security Enhancements (Optional)

**For Production:**

1. **Authentication/Authorization**
```python
from fastapi import Security, HTTPBearer

security = HTTPBearer()

@app.post("/predict")
async def predict(data: PredictionRequest, credentials: HTTPAuthCredential = Security(security)):
    verify_token(credentials.credentials)
    # ... prediction logic
```

2. **Rate Limiting**
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/predict")
@limiter.limit("100/minute")
async def predict(request: Request, data: PredictionRequest):
    # ... prediction logic
```

3. **CORS Restriction**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://trusted-domain.com"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)
```

4. **TLS/HTTPS**
```bash
# Use reverse proxy (Nginx/Traefik) or
# Let's Encrypt with Certbot
```

5. **Input Sanitization**
```python
# Pydantic already handles this
# Additionally: check for NaN, Infinity
@validator('feature_1')
@classmethod
def validate_feature(cls, v):
    if not isfinite(v):
        raise ValueError('Feature must be finite')
    return v
```

---

## 📝 Design Decisions & Rationale

| Decision | Rationale | Alternative |
|----------|-----------|-------------|
| FastAPI over Flask | Type hints, async support, auto docs | Flask (simpler but less performance) |
| Pydantic validation | Automatic, type-safe, integrated | Manual validation (error-prone) |
| Load model at startup | Fail-fast, Kubernetes-friendly | Lazy loading (slower first request) |
| Prometheus metrics | Industry standard, Grafana integration | Custom logging (harder to analyze) |
| Single/batch endpoints | Both patterns useful for different scenarios | Single endpoint for all (less efficient) |
| Kubernetes manifests | Production-ready, auto-scaling | Manual scaling (admin overhead) |
| 30 feature input | Dataset requirement (breast cancer) | Variable features (require schema) |

---

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Scikit-learn Documentation](https://scikit-learn.org/)

---

## 🎯 Next Steps

1. **Test the API**: Use [CHEATSHEET.md](CHEATSHEET.md) commands
2. **Monitor**: Set up Grafana dashboards
3. **Scale**: Adjust replicas in `fastapi-deployment.yaml`
4. **Secure**: Add authentication/HTTPS for production
5. **Extend**: Add new endpoints or model versions

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: ✅ Production Ready
