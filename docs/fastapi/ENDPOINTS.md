# 📡 FastAPI Endpoints Reference

Detailed documentation of all 13 FastAPI endpoints for the ML model serving API.

---

## 📑 Endpoint Index

| Category | Endpoint | Method | Purpose |
|----------|----------|--------|---------|
| **Health** | `/health` | GET | Kubernetes liveness probe |
| **Health** | `/ping` | GET | MLflow compatibility check |
| **Model Info** | `/model/metadata` | GET | Model information & metrics |
| **Model Info** | `/model/features` | GET | Expected feature names |
| **Prediction** | `/predict` | POST | Single prediction |
| **Prediction** | `/batch-predict` | POST | Batch predictions |
| **Prediction** | `/invocations` | POST | MLflow-compatible format |
| **Metrics** | `/metrics` | GET | Prometheus metrics |
| **Metrics** | `/prometheus-metrics` | GET | Explicit Prometheus format |
| **Docs** | `/docs` | GET | Swagger UI interactive docs |
| **Docs** | `/redoc` | GET | ReDoc alternative docs |
| **Root** | `/` | GET | API information & links |
| **OpenAPI** | `/openapi.json` | GET | OpenAPI specification |

---

## 1️⃣ Health & Status Endpoints

### GET `/health`

**Purpose**: Kubernetes liveness probe. Check if API is alive and ready.

**Status Code**: `200 OK`

**Response Body**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

**Response Schema**:
```python
class HealthResponse(BaseModel):
    status: str          # "healthy" or "unhealthy"
    version: str         # API version
    model_loaded: bool   # True if model is available
    timestamp: str       # ISO 8601 timestamp
```

**Usage**:
```bash
# Simple check
curl http://127.0.0.1:8000/health

# Kubernetes probe definition
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

**Notes**:
- Returns 200 even if model not loaded (to prevent pod restart loops)
- Check `model_loaded` field for actual model availability
- Used by Kubernetes for container health monitoring

---

### GET `/ping`

**Purpose**: MLflow compatibility check. Minimal response for quick checks.

**Status Code**: `200 OK`

**Response Body**:
```json
{
  "ping": "pong"
}
```

**Usage**:
```bash
# Quick compatibility check
curl http://127.0.0.1:8000/ping

# Kubernetes readiness probe
readinessProbe:
  httpGet:
    path: /ping
    port: 8000
  initialDelaySeconds: 20
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

**Notes**:
- Lightest endpoint (minimal overhead)
- MLflow model server compatible
- Used for readiness probe (traffic admission decision)

---

## 2️⃣ Model Information Endpoints

### GET `/model/metadata`

**Purpose**: Get model information (accuracy, F1-score, classes, etc.)

**Status Code**: `200 OK`

**Response Body**:
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

**Response Schema**:
```python
class ModelMetadata(BaseModel):
    name: str              # Model name
    version: str           # Model version
    accuracy: float        # Accuracy metric (0-1)
    f1_score: float        # F1-score (0-1)
    classes: List[str]     # Prediction classes
    n_features: int        # Number of input features
```

**Usage**:
```bash
# Get model metadata
curl -s http://127.0.0.1:8000/model/metadata | jq .

# Extract specific info
curl -s http://127.0.0.1:8000/model/metadata | jq '.accuracy'
# Output: 0.92
```

**Error Responses**:

**404 Not Found** - Model not available
```json
{
  "detail": "Model not found",
  "status": 404
}
```

**Notes**:
- Metadata loaded from `artifacts/model/metadata.json`
- Classes usually: `["class_0", "class_1"]` for binary classification
- Accuracies and F1-scores from training evaluation

---

### GET `/model/features`

**Purpose**: Get expected feature names for input validation.

**Status Code**: `200 OK`

**Response Body**:
```json
{
  "features": [
    "mean radius",
    "mean texture",
    "mean perimeter",
    "mean area",
    "mean smoothness",
    ... (30 total features)
  ]
}
```

**Response Schema**:
```python
class FeaturesResponse(BaseModel):
    features: List[str]    # Feature names (exactly 30)
```

**Usage**:
```bash
# Get all feature names
curl -s http://127.0.0.1:8000/model/features | jq '.features | length'
# Output: 30

# Get first 5 features
curl -s http://127.0.0.1:8000/model/features | jq '.features[:5]'
# Output: ["mean radius", "mean texture", "mean perimeter", "mean area", "mean smoothness"]

# Check if feature exists
curl -s http://127.0.0.1:8000/model/features | jq '.features | contains(["mean radius"])'
# Output: true
```

**Error Responses**:

**404 Not Found** - Model metadata not available
```json
{
  "detail": "Model metadata not found"
}
```

**Notes**:
- Features from breast cancer dataset
- Order matters for prediction requests
- Use for building front-end forms or API clients

---

## 3️⃣ Prediction Endpoints

### POST `/predict`

**Purpose**: Single prediction with 30 input features.

**Status Code**: `200 OK` (success) | `400 Bad Request` (validation error)

**Request Body**:
```json
{
  "feature_1": 13.54,
  "feature_2": 14.36,
  "feature_3": 87.46,
  ... (30 features total, all required)
}
```

**Request Schema**:
```python
class PredictionRequest(BaseModel):
    feature_1: float      # Required
    feature_2: float      # Required
    # ... feature_3 to feature_30 (all required)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "feature_1": 0.5, ..., "feature_30": 0.3
            }
        }
    )
```

**Response Body**:
```json
{
  "prediction": 1,
  "probability": [0.08, 0.92],
  "confidence": 0.92,
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

**Response Schema**:
```python
class PredictionResponse(BaseModel):
    prediction: int        # Predicted class (0 or 1)
    probability: List[float]  # Probability for each class
    confidence: float      # Max probability
    timestamp: str         # Prediction timestamp
```

**Usage**:
```bash
# Save request to file
cat > /tmp/request.json << 'EOF'
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
  -d @/tmp/request.json | jq .
```

**Error Responses**:

**400 Bad Request** - Missing features
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "feature_15"],
      "msg": "Field required"
    }
  ]
}
```

**400 Bad Request** - Wrong type
```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["body", "feature_5"],
      "msg": "Input should be a valid integer"
    }
  ]
}
```

**404 Not Found** - Model not available
```json
{
  "detail": "Model not loaded"
}
```

**Metrics Tracked**:
- `prediction_requests_total{endpoint="predict"}` - Total requests
- `prediction_latency_seconds{endpoint="predict"}` - Response time
- `prediction_requests_successful{endpoint="predict"}` - Success count
- `prediction_requests_failed{endpoint="predict"}` - Error count

**Performance**:
- Expected latency: 5-15ms (p95)
- Throughput: ~100 predictions/sec per pod

**Notes**:
- All 30 features required (no defaults)
- Features must be numeric (float or int)
- No NaN or infinity values allowed
- Feature order matters (must match training data)

---

### POST `/batch-predict`

**Purpose**: Batch predictions for multiple samples (1-1000 records).

**Status Code**: `200 OK` (success) | `400 Bad Request` (validation error)

**Request Body**:
```json
{
  "records": [
    {
      "feature_1": 13.54, "feature_2": 14.36, ..., "feature_30": 0.1193
    },
    {
      "feature_1": 9.504, "feature_2": 12.44, ..., "feature_30": 0.1404
    }
  ]
}
```

**Request Schema**:
```python
class BatchPredictionRequest(BaseModel):
    records: List[PredictionRequest]  # 1-1000 items
    
    @field_validator('records')
    @classmethod
    def validate_batch_size(cls, v):
        if len(v) > 1000:
            raise ValueError('Maximum 1000 records allowed')
        if len(v) < 1:
            raise ValueError('At least 1 record required')
        return v
```

**Response Body**:
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

**Response Schema**:
```python
class BatchPredictionResponse(BaseModel):
    predictions: List[Dict[str, Union[int, List[float], float]]]
    processing_time_ms: float  # Total processing time
    total_records: int         # Number of records processed
```

**Usage**:
```bash
# Batch prediction (5 samples)
curl -X POST http://127.0.0.1:8000/batch-predict \
  -H "Content-Type: application/json" \
  -d '{
    "records": [
      {"feature_1": 0.5, ..., "feature_30": 0.3},
      {"feature_1": 0.2, ..., "feature_30": 0.8},
      {"feature_1": 0.7, ..., "feature_30": 0.4},
      {"feature_1": 0.4, ..., "feature_30": 0.6},
      {"feature_1": 0.9, ..., "feature_30": 0.2}
    ]
  }' | jq .

# Extract predictions
curl -s ... | jq '.predictions[].prediction'
# Output:
# 1
# 0
# 1
# 0
# 1
```

**Error Responses**:

**400 Bad Request** - Empty batch
```json
{
  "detail": "At least 1 record required"
}
```

**400 Bad Request** - Batch too large
```json
{
  "detail": "Maximum 1000 records allowed"
}
```

**400 Bad Request** - Invalid record
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "records", 2, "feature_10"],
      "msg": "Field required"
    }
  ]
}
```

**Metrics Tracked**:
- `prediction_requests_total{endpoint="batch_predict"}` - Total requests
- `prediction_latency_seconds{endpoint="batch_predict"}` - Response time
- `batch_size_requests` - Distribution of batch sizes

**Performance**:
- 1 record: ~10ms
- 10 records: ~15ms (1.5ms per record)
- 100 records: ~120ms (1.2ms per record)
- 1000 records: ~1200ms (1.2ms per record)
- Throughput: ~1000 predictions/sec total

**Optimization Tips**:
- Batch 10-100 items for optimal efficiency
- Avoid batch > 1000 (memory limits)
- Monitor `processing_time_ms` for performance regressions

**Notes**:
- Each record must have all 30 features
- Records processed sequentially, NOT in parallel
- If one record fails, entire batch fails (all-or-nothing)

---

### POST `/invocations`

**Purpose**: MLflow-compatible prediction endpoint. Supports MLflow's dataframe_split format.

**Status Code**: `200 OK` (success) | `400 Bad Request` (validation error)

**Request Body** (MLflow format):
```json
{
  "dataframe_split": {
    "columns": [
      "mean radius", "mean texture", ..., "worst fractal dimension"
    ],
    "data": [
      [13.54, 14.36, 87.46, ..., 0.1193],
      [9.504, 12.44, 65.24, ..., 0.1404]
    ]
  }
}
```

**Response Body** (MLflow format):
```json
{
  "predictions": [
    [0, [0.92, 0.08]],
    [1, [0.15, 0.85]]
  ]
}
```

**Request Schema**:
```python
class DataFrameSplitRequest(BaseModel):
    dataframe_split: Dict[str, Union[List[str], List[List[float]]]]
    # columns: exact feature names
    # data: array of arrays (each row = sample)
```

**Usage**:
```bash
# MLflow model serving format
curl -X POST http://127.0.0.1:8000/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "dataframe_split": {
      "columns": ["mean radius", "mean texture", ..., "worst fractal dimension"],
      "data": [[13.54, 14.36, 87.46, ..., 0.1193]]
    }
  }'

# Output:
# {"predictions": [[1, [0.08, 0.92]]]}
```

**Compatibility**:
```bash
# MLflow command line
mlflow models predict -m models/model \
  -i input.json \
  -t dataframe_split

# Python SDK
mlflow.pyfunc.load_model("models/model").predict(data)
```

**Notes**:
- Exact column names required
- Used for MLflow model serving compatibility
- Response format: [prediction, [probability_class0, probability_class1]]
- Functionally equivalent to `/batch-predict`, different format

---

## 4️⃣ Monitoring Endpoints

### GET `/metrics`

**Purpose**: Prometheus metrics in text format. Scraped by Prometheus server.

**Status Code**: `200 OK` with `text/plain` content type

**Response Format**: Prometheus text format
```
# HELP prediction_requests_total Total number of prediction requests
# TYPE prediction_requests_total counter
prediction_requests_total{endpoint="predict"} 127.0
prediction_requests_total{endpoint="batch_predict"} 34.0

# HELP prediction_latency_seconds Prediction processing latency in seconds
# TYPE prediction_latency_seconds histogram
prediction_latency_seconds_bucket{endpoint="predict",le="0.001"} 0.0
prediction_latency_seconds_bucket{endpoint="predict",le="0.005"} 15.0
...
```

**Usage**:
```bash
# View all metrics
curl -s http://127.0.0.1:8000/metrics

# Filter metrics
curl -s http://127.0.0.1:8000/metrics | grep prediction_requests_total

# Count lines
curl -s http://127.0.0.1:8000/metrics | wc -l

# Get specific metric
curl -s http://127.0.0.1:8000/metrics | grep "^model_loaded"
```

**Prometheus Configuration**:
```yaml
scrape_configs:
  - job_name: 'fastapi-api'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['localhost:8000']
```

**Metrics Categories**:

**Counters:**
- `prediction_requests_total{endpoint="predict"}` - Total requests
- `prediction_requests_successful{endpoint="predict"}` - Successful
- `prediction_requests_failed{endpoint="predict"}` - Failed

**Histograms:**
- `prediction_latency_seconds_bucket` - Latency distribution with buckets
- `batch_size_requests_bucket` - Batch size distribution

**Gauges:**
- `model_loaded` - 1 = loaded, 0 = not loaded
- `api_uptime_seconds` - API uptime in seconds

**Response Time**: <10ms (very fast)

**Notes**:
- Used by Prometheus scraper
- Default scrape interval: 30 seconds
- Includes Python runtime metrics (gc, memory)

---

### GET `/prometheus-metrics`

**Purpose**: Explicit Prometheus metrics endpoint (alternative to `/metrics`).

**Status Code**: `200 OK`

**Response Format**: Same as `/metrics` endpoint

**Usage**:
```bash
curl -s http://127.0.0.1:8000/prometheus-metrics | grep prediction
```

**Notes**:
- Identical to `/metrics`
- Provided for explicit clarity
- Use either endpoint

---

## 5️⃣ Documentation Endpoints

### GET `/docs`

**Purpose**: Interactive Swagger UI for API testing and exploration.

**Status Code**: `200 OK` (returns HTML)

**Access**:
```
http://127.0.0.1:8000/docs
```

**Features**:
- ✅ Browse all endpoints
- ✅ View request/response schemas
- ✅ Test endpoints directly
- ✅ See real-time responses
- ✅ Download OpenAPI spec

**Screenshots**:
```
[Try it Out] → [Execute] → [Response: 200 OK]
```

**Notes**:
- Auto-generated from FastAPI
- Requires JavaScript enabled
- No authentication needed (unless added)

---

### GET `/redoc`

**Purpose**: Alternative documentation format using ReDoc.

**Status Code**: `200 OK` (returns HTML)

**Access**:
```
http://127.0.0.1:8000/redoc
```

**Features**:
- ✅ Beautiful documentation layout
- ✅ Better for printing
- ✅ Organized by tags
- ✅ No "try it" feature (view-only)

**Notes**:
- Good for sharing documentation
- Better for mobile viewing
- Read-only (no testing)

---

### GET `/openapi.json`

**Purpose**: OpenAPI specification in JSON format.

**Status Code**: `200 OK` with `application/json` content type

**Usage**:
```bash
# Download OpenAPI spec
curl -s http://127.0.0.1:8000/openapi.json > openapi.json

# Generate client code
openapi-generator-cli generate -i openapi.json -g python-client -o python_client

# Validate spec
npx swagger-cli validate openapi.json
```

**Notes**:
- Can be used to generate client libraries
- Import into API management tools (AWS API Gateway, Kong, etc.)
- Useful for API documentation generation

---

## 6️⃣ Root Endpoint

### GET `/`

**Purpose**: API information and links to endpoints.

**Status Code**: `200 OK`

**Response Body**:
```json
{
  "title": "MLflow Model Serving API",
  "version": "1.0.0",
  "description": "REST API for serving ML model predictions",
  "documentation": {
    "swagger_ui": "http://127.0.0.1:8000/docs",
    "redoc": "http://127.0.0.1:8000/redoc",
    "openapi_spec": "http://127.0.0.1:8000/openapi.json"
  },
  "endpoints": {
    "health": "http://127.0.0.1:8000/health",
    "predict": "http://127.0.0.1:8000/predict",
    "batch_predict": "http://127.0.0.1:8000/batch-predict",
    "metrics": "http://127.0.0.1:8000/metrics"
  }
}
```

**Usage**:
```bash
curl -s http://127.0.0.1:8000/ | jq .
```

**Notes**:
- Good entry point for API discovery
- Links to documentation
- Provides endpoint overview

---

## 📊 Request/Response Statistics

| Endpoint | Method | Avg Latency | Throughput | Size |
|----------|--------|-------------|------------|------|
| `/health` | GET | 1ms | 10k/s | <100B |
| `/ping` | GET | 1ms | 10k/s | <100B |
| `/model/metadata` | GET | 2ms | 5k/s | ~500B |
| `/model/features` | GET | 2ms | 5k/s | ~500B |
| `/predict` | POST | 10ms | 100/s | ~2KB |
| `/batch-predict` (10) | POST | 15ms | 70/s | ~20KB |
| `/batch-predict` (100) | POST | 120ms | 8/s | ~200KB |
| `/batch-predict` (1000) | POST | 1200ms | 1/s | ~2MB |
| `/invocations` | POST | 10ms | 100/s | ~2KB |
| `/metrics` | GET | 5ms | 200/s | ~5KB |
| `/docs` | GET | 10ms | 100/s | ~500KB |

---

## 🧪 Request Examples by Language

### Python (requests library)
```python
import requests

# Single prediction
r = requests.post('http://127.0.0.1:8000/predict', json={...})
print(r.json())  # {'prediction': 1, 'probability': [...], ...}
```

### JavaScript (fetch API)
```javascript
const response = await fetch('http://127.0.0.1:8000/predict', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({feature_1: 0.5, ...})
});
const result = await response.json();
```

### cURL
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"feature_1": 0.5, ...}'
```

### Go
```go
import "net/http"
client := &http.Client{}
req, _ := http.NewRequest("POST", "http://127.0.0.1:8000/predict", body)
resp, _ := client.Do(req)
```

---

## 🔄 Endpoint Call Flow

```
┌─────────────────┐
│  HTTP Request   │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Route Matching      │
│ (path + method)     │
└────────┬────────────┘
         │ ✗ No match
         ├──────────► 404 Not Found
         │ ✓ Match
         ▼
┌─────────────────────┐
│ Pydantic Validate   │
│ Request Schema      │
└────────┬────────────┘
         │ ✗ Invalid
         ├──────────► 400 Bad Request
         │ ✓ Valid
         ▼
┌─────────────────────┐
│ Execute Endpoint    │
│ Logic               │
└────────┬────────────┘
         │ ✗ Error
         ├──────────► 500 Error
         │ ✓ Success
         ▼
┌─────────────────────┐
│ Collect Metrics     │
│ (Prometheus)        │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Serialize Response  │
│ (Pydantic)          │
└────────┬────────────┘
         │
         ▼
┌──────────────────────┐
│ Return HTTP Response │
│ (JSON)               │
└──────────────────────┘
```

---

## ✅ Checklist for Using the API

- [ ] API is running (`curl http://127.0.0.1:8000/health`)
- [ ] Model is loaded (check `model_loaded` field in `/health`)
- [ ] All 30 features provided in prediction request
- [ ] Features are numeric (float/int)
- [ ] Batch size <= 1000 records
- [ ] Using correct endpoint (`/predict` for single, `/batch-predict` for batch)
- [ ] Content-Type header is `application/json` for POST requests
- [ ] Monitoring metrics are being collected (`/metrics` returns data)

---

**Last Updated**: 2024  
**API Version**: 1.0.0  
**Status**: ✅ Production Ready
