"""MLflow utilities to handle client-server artifact synchronization."""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional

import mlflow


def is_remote_tracking_uri(tracking_uri: str) -> bool:
    """Check if the tracking URI is a remote HTTP server."""
    return tracking_uri.startswith('http://') or tracking_uri.startswith('https://')


def prepare_artifact_for_remote_logging(artifact_path: str) -> str:
    """
    For remote MLflow servers, this function prepares an artifact by copying it
    to a temporary location that the server can access via HTTP upload.
    
    When using a remote MLflow server (HTTP), the client cannot directly access
    the server's filesystem paths (like /mlruns). Instead, artifacts are uploaded
    via HTTP.
    
    However, mlflow.log_model() attempts to write to the artifact store directly,
    which fails with permission errors when the server's paths aren't accessible
    to the client.
    
    This function doesn't actually solve that - the real solution is to either:
    1. Run training inside the container (same path context as server)
    2. Use an S3-compatible artifact store (Minio, AWS S3, etc.)
    3. configure the server to accept HTTP artifact uploads
    
    For now, we just return the original path and let the error handling in
    train.py deal with the permission error gracefully.
    """
    return artifact_path


def log_model_with_fallback(
    sk_model,
    model_path: str,
    tracking_uri: Optional[str] = None,
    run_name: str = 'model'
):
    """
    Log a model to MLflow with graceful fallback for remote servers.
    
    When the tracking URI is a remote HTTP server, attempting to log a model
    via filesystem operations will fail with permission errors. This function
    attempts the log operation and provides clear feedback if it fails.
    
    Args:
        sk_model: The trained model to log
        model_path: Path where the model was already saved locally
        tracking_uri: The MLflow tracking URI (optional)
        run_name: Name for the model in MLflow
        
    Returns:
        bool: True if logging succeeded, False otherwise
    """
    if tracking_uri is None:
        tracking_uri = mlflow.get_tracking_uri()
    
    is_remote = is_remote_tracking_uri(tracking_uri)
    
    try:
        mlflow.sklearn.log_model(sk_model=sk_model, name=run_name)
        return True
    except PermissionError as e:
        if is_remote:
            print(f"⚠️  WARNING: Cannot log model to remote MLflow server")
            print(f"   Error: {e}")
            print(f"   This is expected when using HTTP-based MLflow servers.")
            print(f"   The model was trained and saved locally at: {model_path}")
            print(f"   To fix this, consider:")
            print(f"   1. Running training inside the MLflow container")
            print(f"   2. Configuring an S3-compatible artifact store (e.g., Minio)")
            print(f"   3. Using a PostgreSQL backend with proper artifact storage")
            return False
        else:
            raise
    except Exception as e:
        print(f"❌ ERROR: Failed to log model to MLflow: {e}")
        print(f"   Model saved locally at: {model_path}")
        return False
