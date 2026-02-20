"""
Pydantic models and schemas for FastAPI endpoints
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PredictionRequest(BaseModel):
    """Request model for prediction endpoint"""
    features: List[float] = Field(
        ...,
        description="List of 30 features for Breast Cancer dataset prediction",
        example=[
            14.0, 20.0, 90.0, 600.0, 0.10,
            0.15, 0.12, 0.07, 0.18, 0.06,
            0.4, 1.2, 3.0, 40.0, 0.01,
            0.02, 0.03, 0.02, 0.03, 0.004,
            16.5, 27.0, 110.0, 850.0, 0.13,
            0.25, 0.22, 0.12, 0.24, 0.08
        ]
    )


class PredictionResponse(BaseModel):
    """Response model for prediction endpoint"""
    prediction: int = Field(
        ...,
        description="Predicted class (0: malignant, 1: benign)"
    )
    probability: float = Field(
        ...,
        description="Probability of the predicted class"
    )
    confidence: float = Field(
        ...,
        description="Overall confidence in the prediction"
    )
    features_count: int = Field(
        ...,
        description="Number of features used"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of prediction"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(
        ...,
        description="Service status",
        example="healthy"
    )
    version: str = Field(
        ...,
        description="API version"
    )
    model_loaded: bool = Field(
        ...,
        description="Whether the ML model is loaded"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of health check"
    )


class ModelMetadata(BaseModel):
    """Response model for model metadata endpoint"""
    name: str = Field(
        ...,
        description="Name of the model",
        example="RandomForestClassifier"
    )
    version: str = Field(
        ...,
        description="Model version"
    )
    trained_date: str = Field(
        ...,
        description="Date model was trained"
    )
    accuracy: float = Field(
        ...,
        description="Model accuracy on test set"
    )
    f1_score: float = Field(
        ...,
        description="F1 score on test set"
    )
    classes: List[str] = Field(
        ...,
        description="Classes the model can predict",
        example=["malignant", "benign"]
    )
    n_features: int = Field(
        ...,
        description="Number of input features expected by the model"
    )
    framework: str = Field(
        ...,
        description="ML framework used",
        example="scikit-learn"
    )


class DataFrameSplitRequest(BaseModel):
    """Request model for dataframe_split format (MLflow standard)"""
    columns: List[str] = Field(
        ...,
        description="Column names"
    )
    data: List[List[float]] = Field(
        ...,
        description="Data in list format"
    )


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint"""
    total_requests: int = Field(
        ...,
        description="Total prediction requests served"
    )
    successful_requests: int = Field(
        ...,
        description="Successful requests"
    )
    failed_requests: int = Field(
        ...,
        description="Failed requests"
    )
    average_latency_ms: float = Field(
        ...,
        description="Average request latency in milliseconds"
    )
    uptime_seconds: float = Field(
        ...,
        description="API uptime in seconds"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of metrics collection"
    )


class ErrorResponse(BaseModel):
    """Response model for error responses"""
    error: str = Field(
        ...,
        description="Error message"
    )
    detail: Optional[str] = Field(
        None,
        description="Detailed error information"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of error"
    )


class BatchPredictionRequest(BaseModel):
    """Request model for batch prediction"""
    predictions: List[PredictionRequest] = Field(
        ...,
        description="List of prediction requests",
        min_items=1,
        max_items=1000
    )


class BatchPredictionResponse(BaseModel):
    """Response model for batch predictions"""
    predictions: List[PredictionResponse] = Field(
        ...,
        description="List of predictions"
    )
    total_processed: int = Field(
        ...,
        description="Total requests processed"
    )
    successful: int = Field(
        ...,
        description="Successful predictions"
    )
    failed: int = Field(
        ...,
        description="Failed predictions"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of batch processing"
    )
