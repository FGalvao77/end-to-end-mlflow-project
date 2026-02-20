#!/usr/bin/env bash
set -euo pipefail

# Script to build image, run MLflow server and serve model locally.
# Usage: ./scripts/run.sh [build|up|down|serve-model]

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
IMAGE_NAME=${IMAGE_NAME:-my-mlflow-app:latest}

build() {
  docker build -t "$IMAGE_NAME" -f src/mlops_project/Dockerfile "$HERE"
}

up() {
  # start MLflow tracking server (host 5001 -> container 5000)
  docker run -d --name mlflow_local -p 5001:5000 \
    -v "$HERE/mlruns":/mlruns:rw \
    -e MLFLOW_BACKEND_STORE_URI=sqlite:////mlruns/mlflow.db \
    -e MLFLOW_DEFAULT_ARTIFACT_ROOT=file:///mlruns/artifacts \
    "$IMAGE_NAME"
  echo "MLflow UI: http://127.0.0.1:5001"
}

serve_model() {
  # serve model from artifacts/model (host 8000 -> container 8000)
  docker run -d --name model_server -p 8000:8000 \
    -v "$HERE/artifacts/model":/model:ro \
    -e SERVE_MODEL=1 -e SERVE_MODEL_PATH=/model \
    "$IMAGE_NAME"
  echo "Model server: http://127.0.0.1:8000/ping"
}

down() {
  docker stop model_server mlflow_local || true
  docker rm -f model_server mlflow_local || true
}

case "${1:-}" in
  build) build ;;
  up) up ;;
  serve-model) serve_model ;;
  down) down ;;
  all)
    build
    down
    up
    serve_model
    ;;
  *)
    echo "Usage: $0 {build|up|serve-model|down|all}"
    exit 1
    ;;
esac
