#!/usr/bin/env sh
set -e

# Default ports
MLFLOW_PORT=${MLFLOW_PORT:-5000}
MODEL_PORT=${MODEL_PORT:-8000}
API_PORT=${API_PORT:-8000}

is_true() {
  case "$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')" in
    1|true|yes|y) return 0 ;;
    *) return 1 ;;
  esac
}

# Determine which service to run
if is_true "${SERVE_API:-0}"; then
  echo "Starting FastAPI model serving on port ${API_PORT}"
  exec python -m uvicorn src.mlops_project.api:app --host 0.0.0.0 --port "${API_PORT}"
  
elif is_true "${SERVE_MODEL:-0}" && [ -n "${SERVE_MODEL_PATH}" ]; then
  echo "Serving MLflow model from ${SERVE_MODEL_PATH} on port ${MODEL_PORT}"
  exec mlflow models serve -m "${SERVE_MODEL_PATH}" -p "${MODEL_PORT}" --host 0.0.0.0 --no-conda
  
else
  echo "Starting MLflow tracking server on port ${MLFLOW_PORT}"
  : "Using backend: ${MLFLOW_BACKEND_STORE_URI:-sqlite:////mlruns/mlflow.db}"
  exec mlflow server --host 0.0.0.0 --port "${MLFLOW_PORT}" \
    --backend-store-uri "${MLFLOW_BACKEND_STORE_URI:-sqlite:////mlruns/mlflow.db}" \
    --default-artifact-root "${MLFLOW_DEFAULT_ARTIFACT_ROOT:-file:///mlruns/artifacts}"
fi
