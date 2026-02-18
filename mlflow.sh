#!/bin/bash
# MLflow Server & Training Helper Script
#
# This script provides convenient commands for running MLflow with the project:
# - mlflow-server: Start MLflow server in Docker
# - mlflow-train-host: Train on host machine (with server) 
# - mlflow-train-container: Train inside container (recommended for remote server)
# - mlflow-ui: View experiments in web browser
# - mlflow-stop: Stop Docker containers
# - mlflow-clean: Clean up artifacts and database
#

set -e

DOCKER_COMPOSE_FILE="src/mlops_project/docker-compose.mlflow.yml"
export DOCKER_API_VERSION=1.44

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Display usage
show_usage() {
    cat << EOF
${BLUE}MLflow Docker Helper${NC}

Usage: $0 [COMMAND]

Commands:
  server              Start MLflow server in Docker
  train-host          Train on host, sync with remote MLflow server
  train-container     Train inside Docker container (RECOMMENDED)
  ui                  Open MLflow UI in browser
  stop                Stop all Docker containers
  clean               Clean artifacts and reset database
  logs                Show MLflow server logs
  help                Show this help message

Examples:
  $0 server               # Start MLflow server
  $0 train-container      # Run training in container (no permission errors)
  $0 ui                   # View experiments
  $0 stop                 # Stop containers

EOF
}

# MLflow Server
mlflow_server() {
    print_header "Starting MLflow server in Docker..."
    docker compose -f "$DOCKER_COMPOSE_FILE" up -d mlflow
    sleep 5
    
    if docker compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "mlflow.*Up"; then
        print_success "MLflow server is running at http://127.0.0.1:5000"
    else
        print_error "Failed to start MLflow server"
        exit 1
    fi
}

# Train on host with remote server
train_host() {
    print_header "Starting training on host (synced with remote MLflow)..."
    if ! docker compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "mlflow.*Up"; then
        print_warning "MLflow server not running. Starting it..."
        mlflow_server
    fi
    
    print_header "Running training script..."
    export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
    .venv/bin/python src/mlops_project/train.py
    
    if grep -q "Permission denied" artifacts/results/evaluation_results.txt 2>/dev/null || \
       grep -q "WARNING: failed to log model" /tmp/train_output.log 2>/dev/null; then
        print_warning "Training completed with permission warnings"
        print_warning "This is expected when training on host with remote MLflow server"
        print_warning "Run '$0 train-container' for a seamless experience"
    else
        print_success "Training completed successfully!"
    fi
}

# Train inside container
train_container() {
    print_header "Starting training inside Docker container..."
    if ! docker compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "mlflow.*Up"; then
        print_warning "MLflow server not running. Starting it..."
        mlflow_server
    fi
    
    print_header "Building and running training service..."
    docker compose -f "$DOCKER_COMPOSE_FILE" --profile training up --build training
    print_success "Training completed! (No permission errors)"
}

# Open UI
open_ui() {
    print_header "Opening MLflow UI..."
    MLFLOW_URL="http://127.0.0.1:5000"
    
    if ! docker compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "mlflow.*Up"; then
        print_error "MLflow server is not running"
        print_warning "Start it with: $0 server"
        exit 1
    fi
    
    # Try to open in browser (works on macOS, Linux with xdg-open)
    if command -v xdg-open &> /dev/null; then
        xdg-open "$MLFLOW_URL"
        print_success "Opening $MLFLOW_URL in browser..."
    elif command -v open &> /dev/null; then
        open "$MLFLOW_URL"
        print_success "Opening $MLFLOW_URL in browser..."
    else
        print_warning "Could not automatically open browser"
        print_warning "Manually open: $MLFLOW_URL"
    fi
}

# Stop all containers
stop_all() {
    print_header "Stopping all containers..."
    docker compose -f "$DOCKER_COMPOSE_FILE" down
    print_success "All containers stopped"
}

# Clean everything
clean_all() {
    print_header "Cleaning artifacts and database..."
    read -p "Are you sure? This will remove all MLflow runs and artifacts. [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf src/mlops_project/mlruns
        mkdir -p src/mlops_project/mlruns/artifacts
        print_success "Cleaned successfully"
    else
        print_warning "Cancelled"
    fi
}

# Show logs
show_logs() {
    print_header "MLflow server logs:"
    docker compose -f "$DOCKER_COMPOSE_FILE" logs --tail=50 mlflow
}

# Main command dispatcher
case "${1:-help}" in
    server)
        mlflow_server
        ;;
    train-host)
        train_host
        ;;
    train-container)
        train_container
        ;;
    ui)
        open_ui
        ;;
    stop)
        stop_all
        ;;
    clean)
        clean_all
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
