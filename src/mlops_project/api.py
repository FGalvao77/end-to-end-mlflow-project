"""
FastAPI application for ML Model Serving
Serves the trained RandomForest model with REST API endpoints
"""

import os
import json
import logging
import joblib
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

from mlops_project.schemas import (
    PredictionRequest,
    PredictionResponse,
    HealthResponse,
    ModelMetadata,
    ErrorResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Prometheus Metrics
# ============================================================================

# Counters
prediction_requests_total = Counter(
    'mlflow_prediction_requests_total',
    'Total prediction requests',
    ['status']
)

successful_predictions = Counter(
    'mlflow_successful_predictions_total',
    'Total successful predictions'
)

failed_predictions = Counter(
    'mlflow_failed_predictions_total',
    'Total failed predictions'
)

# Histograms
prediction_latency = Histogram(
    'mlflow_prediction_latency_seconds',
    'Prediction latency in seconds',
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

batch_size_histogram = Histogram(
    'mlflow_batch_size',
    'Batch size for batch predictions',
    buckets=(1, 5, 10, 50, 100, 500, 1000)
)

# Gauges
api_uptime_seconds = Gauge(
    'mlflow_api_uptime_seconds',
    'API uptime in seconds'
)

model_loaded_gauge = Gauge(
    'mlflow_model_loaded',
    'Whether the model is currently loaded'
)

# ============================================================================
# Global Variables
# ============================================================================

model = None
model_metadata = {}
start_time = None
feature_names = []

# ============================================================================
# Model Loading
# ============================================================================

def load_model() -> bool:
    """Load the trained model from artifacts directory"""
    global model, model_metadata, feature_names
    
    try:
        # Try to load from artifacts directory
        project_root = Path(__file__).resolve().parent.parent.parent
        model_path = project_root / "artifacts" / "model" / "model.joblib"
        metadata_path = project_root / "artifacts" / "model" / "metadata.json"
        
        if not model_path.exists():
            logger.error(f"Model file not found at {model_path}")
            model_loaded_gauge.set(0)
            return False
        
        model = joblib.load(model_path)
        logger.info(f"Model loaded successfully from {model_path}")
        
        # Load model metadata dynamically
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                model_metadata = json.load(f)
            logger.info(f"Model metadata loaded from {metadata_path}")
        else:
            logger.warning(f"Metadata file not found at {metadata_path}. Using inferred metadata.")
            model_metadata = {
                "name": getattr(model, 'name', 'UnknownModel'), # Use 'name' key for FastAPI schema
                "version": "Unknown",
                "accuracy": 0.0,
                "f1_score": 0.0,
                "classes": ["Unknown"],
                "n_features": 0,
                "framework": "scikit-learn",
                "trained_date": datetime.now().isoformat()
            }

        # Dynamically get feature names and classes from the loaded model
        if hasattr(model, 'n_features_in_'):
            model_metadata["n_features"] = model.n_features_in_
            feature_names = [f"feature_{i}" for i in range(model.n_features_in_)]
        elif "n_features" in model_metadata:
            feature_names = [f"feature_{i}" for i in range(model_metadata["n_features"])]
        else:
            logger.warning("Could not determine number of features from model or metadata. Defaulting to 30.")
            model_metadata["n_features"] = 30
            feature_names = [f"feature_{i}" for i in range(30)]

        if hasattr(model, 'classes_'):
            model_metadata["classes"] = [str(c) for c in model.classes_]
        elif "classes" not in model_metadata:
            logger.warning("Could not determine classes from model or metadata. Defaulting to ['malignant', 'benign'].")
            model_metadata["classes"] = ["malignant", "benign"]

        # Ensure model_metadata has all fields required by ModelMetadata schema
        # Fill missing fields with defaults or derived values
        if "name" not in model_metadata:
             model_metadata["name"] = getattr(model, 'name', 'RandomForestClassifier').__class__.__name__ if model else "UnknownModel"
        if "accuracy" not in model_metadata:
            model_metadata["accuracy"] = 0.0 # Will be updated by evaluate.py
        if "f1_score" not in model_metadata:
            model_metadata["f1_score"] = 0.0 # Will be updated by evaluate.py
        if "version" not in model_metadata:
            model_metadata["version"] = "1.0.0"
        if "trained_date" not in model_metadata:
            model_metadata["trained_date"] = datetime.now().isoformat()
        if "framework" not in model_metadata:
            model_metadata["framework"] = "scikit-learn"
        
        model_loaded_gauge.set(1)
        return True
        
    except Exception as e:
        logger.error(f"Failed to load model or metadata: {e}")
        model_loaded_gauge.set(0)
        return False


# ============================================================================
# Lifespan Events
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI application startup and shutdown"""
    global start_time
    
    # Startup
    logger.info("Starting MLflow Model Serving API...")
    start_time = time.time()
    
    if not load_model():
        logger.error("Failed to load model on startup")
        raise RuntimeError("Model loading failed")
    
    logger.info("API startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MLflow Model Serving API...")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="MLflow Model Serving API",
    description="REST API for serving trained ML model with real-time predictions",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Middleware for Metrics
# ============================================================================

@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Middleware to track request latency"""
    start_time_request = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time_request
        
        # Update uptime gauge
        if start_time:
            api_uptime_seconds.set(time.time() - start_time)
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        logger.error(f"Middleware error: {e}")
        raise


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint
    Returns the status of the API and model
    
    Used by Kubernetes liveness and readiness probes
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model_loaded=model is not None,
        timestamp=datetime.now()
    )


@app.get("/ping", tags=["Health"])
async def ping():
    """
    Ping endpoint (compatibility with MLflow serving)
    """
    return {"status": "pong"}


# ============================================================================
# Model Information Endpoints
# ============================================================================

@app.get("/model/metadata", response_model=ModelMetadata, tags=["Model Info"])
async def get_model_metadata() -> ModelMetadata:
    """
    Get model metadata and information
    
    Returns:
    - Model name and type
    - Accuracy and F1 score- Version and training date
    - Expected number of features
    """
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    return ModelMetadata(
        model_name=model_metadata.get("name", "Unknown"),
        model_type=model_metadata.get("framework", "Unknown"), # Assuming framework can map to model_type conceptually
        version=model_metadata.get("version", "Unknown"),
        trained_date=model_metadata.get("trained_date", "Unknown"),
        accuracy=model_metadata.get("accuracy", 0.0),
        f1_score=model_metadata.get("f1_score", 0.0),
        classes=model_metadata.get("classes", []),
        n_features=model_metadata.get("n_features", 0),
        framework=model_metadata.get("framework", "Unknown")
    )


@app.get("/model/features", tags=["Model Info"])
async def get_features() -> dict:
    """
    Get expected features for the model
    """
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    return {
        "features": feature_names,
        "count": len(feature_names),
        "description": "Breast Cancer Dataset Features"
    }


# ============================================================================
# Prediction Endpoints
# ============================================================================

@app.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["Predictions"],
    responses={
        503: {"model": ErrorResponse},
        422: {"model": ErrorResponse}
    }
)
async def predict(request: PredictionRequest) -> PredictionResponse:
    """
    Make a single prediction
    
    Request body:
    - features: List of 30 float values (breast cancer features)
    
    Returns:
    - prediction: 0 (malignant) or 1 (benign)
    - probability: Confidence level (0.0 to 1.0)
    - confidence: Overall prediction confidence
    - timestamp: When prediction was made
    
    Example:
    ```json
    {
      "features": [14.0, 20.0, 90.0, ...]  # 30 values
    }
    ```
    """
    if model is None:
        prediction_requests_total.labels(status='error').inc()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    try:
        # Validate input
        if len(request.features) != 30:
            prediction_requests_total.labels(status='error').inc()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Expected 30 features, got {len(request.features)}"
            )
        
        # Record latency
        start_time_pred = time.time()
        
        # Make prediction
        prediction = model.predict([request.features])[0]
        probabilities = model.predict_proba([request.features])[0]
        
        latency = time.time() - start_time_pred
        prediction_latency.observe(latency)
        successful_predictions.inc()
        prediction_requests_total.labels(status='success').inc()
        
        # Return response
        return PredictionResponse(
            prediction=int(prediction),
            probability=float(probabilities[int(prediction)]),
            confidence=float(max(probabilities)),
            features_count=len(request.features),
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        failed_predictions.inc()
        prediction_requests_total.labels(status='error').inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post(
    "/batch-predict",
    response_model=BatchPredictionResponse,
    tags=["Predictions"],
    responses={503: {"model": ErrorResponse}}
)
async def batch_predict(request: BatchPredictionRequest) -> BatchPredictionResponse:
    """
    Make batch predictions
    
    Request body:
    - predictions: List of prediction requests (1-1000 items)
    
    Returns:
    - predictions: List of prediction responses
    - total_processed: Number of predictions made
    - successful: Number of successful predictions
    - failed: Number of failed predictions
    """
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    batch_size_histogram.observe(len(request.predictions))
    
    results = []
    successful = 0
    failed = 0
    
    for pred_req in request.predictions:
        try:
            # Validate input
            if len(pred_req.features) != 30:
                failed += 1
                continue
            
            # Make prediction
            start_time_pred = time.time()
            prediction = model.predict([pred_req.features])[0]
            probabilities = model.predict_proba([pred_req.features])[0]
            latency = time.time() - start_time_pred
            
            prediction_latency.observe(latency)
            
            results.append(
                PredictionResponse(
                    prediction=int(prediction),
                    probability=float(probabilities[int(prediction)]),
                    confidence=float(max(probabilities)),
                    features_count=len(pred_req.features),
                    timestamp=datetime.now()
                )
            )
            successful += 1
            successful_predictions.inc()
            
        except Exception as e:
            logger.error(f"Batch prediction error for item: {e}")
            failed += 1
            failed_predictions.inc()
    
    prediction_requests_total.labels(status='success').inc()
    
    return BatchPredictionResponse(
        predictions=results,
        total_processed=len(request.predictions),
        successful=successful,
        failed=failed,
        timestamp=datetime.now()
    )


# ============================================================================
# MLflow Compatible Endpoints
# ============================================================================

@app.post("/invocations", tags=["MLflow Compatible"])
async def invocations(request: dict):
    """
    MLflow models serving compatible endpoint
    
    Accepts either:
    1. dataframe_split format: {"columns": [...], "data": [...]}
    2. dataframe_records format: [{"col": val, ...}, ...]
    3. instances format: [...]
    """
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    try:
        # Handle dataframe_split format
        if "dataframe_split" in request:
            data = request["dataframe_split"]["data"]
        # Handle instances format
        elif "instances" in request:
            data = request["instances"]
        # Direct list format
        else:
            data = request if isinstance(request, list) else [request]
        
        if not data:
            raise ValueError("No data provided")
        
        # Make predictions
        predictions = model.predict(data)
        probabilities = model.predict_proba(data)
        
        # Return predictions
        successful_predictions.inc()
        prediction_requests_total.labels(status='success').inc()
        
        return {
            "predictions": predictions.tolist(),
            "probabilities": probabilities.tolist()
        }
        
    except Exception as e:
        logger.error(f"MLflow invocations error: {e}")
        failed_predictions.inc()
        prediction_requests_total.labels(status='error').inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# Metrics Endpoint (Prometheus)
# ============================================================================

@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Prometheus metrics endpoint
    
    Exposes:
    - Prediction counters (total, successful, failed)
    - Latency histogram
    - Batch size histogram
    - API uptime gauge
    - Model loaded gauge
    """
    return app.user_data.get("prometheus_metrics", generate_latest())


# Custom metrics endpoint to fix prometheus format
@app.get("/prometheus-metrics", tags=["Monitoring"])
async def prometheus_metrics():
    """
    Prometheus metrics endpoint (alternative format)
    """
    return JSONResponse(
        content=generate_latest().decode('utf-8'),
        media_type="text/plain; version=0.0.4"
    )


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "MLflow Model Serving API",
        "version": "1.0.0",
        "description": "REST API for serving trained ML models",
        "endpoints": {
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/health",
            "predictions": "/predict",
            "batch_predictions": "/batch-predict",
            "model_info": "/model/metadata",
            "metrics": "/metrics"
        }
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
