#!/bin/bash

# Monitoring Setup and Deployment Script
# Script para Configuração e Implantação de Monitoramento
# 
# Usage: bash scripts/monitoring.sh [command]
# Uso: bash scripts/monitoring.sh [comando]

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="mlflow-prod"
MONITORING_DIR="k8s/monitoring"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl."
        exit 1
    fi
    
    # Check kube connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Please configure kubectl."
        exit 1
    fi
    
    # Check namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_warn "Namespace '$NAMESPACE' does not exist. Will be created during deployment."
    fi
    
    log_success "Prerequisites check passed"
}

deploy_monitoring() {
    log_info "Deploying monitoring stack..."
    
    # Create namespace if it doesn't exist
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_info "Creating namespace '$NAMESPACE'..."
        kubectl create namespace "$NAMESPACE"
    fi
    
    # Deploy Prometheus config and rules
    log_info "Deploying Prometheus configuration..."
    kubectl apply -f "$PROJECT_ROOT/$MONITORING_DIR/prometheus-config.yaml"
    
    # Deploy Prometheus and Grafana
    log_info "Deploying Prometheus and Grafana..."
    kubectl apply -f "$PROJECT_ROOT/$MONITORING_DIR/prometheus-grafana-deployment.yaml"
    
    log_success "Monitoring stack deployed"
}

wait_for_deployment() {
    local deployment=$1
    local timeout=${2:-300}
    
    log_info "Waiting for deployment '$deployment' to be ready (timeout: ${timeout}s)..."
    kubectl rollout status deployment/"$deployment" -n "$NAMESPACE" --timeout="${timeout}s"
    log_success "Deployment '$deployment' is ready"
}

verify_deployment() {
    log_info "Verifying monitoring deployment..."
    
    log_info "Waiting for Prometheus..."
    wait_for_deployment "prometheus"
    
    log_info "Waiting for Grafana..."
    wait_for_deployment "grafana"
    
    log_success "All monitoring services deployed and ready"
}

get_prometheus_url() {
    log_info "Prometheus URLs:"
    
    # NodePort
    local nodeport=$(kubectl get svc prometheus -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].nodePort}')
    echo "  NodePort:    http://<NODE_IP>:$nodeport"
    
    # Minikube
    if command -v minikube &> /dev/null; then
        local minikube_ip=$(minikube ip 2>/dev/null || echo "N/A")
        if [ "$minikube_ip" != "N/A" ]; then
            echo "  Minikube:    http://$minikube_ip:$nodeport"
        fi
    fi
    
    echo "  Port-forward: kubectl port-forward svc/prometheus -n $NAMESPACE 9090:9090"
    echo "               http://127.0.0.1:9090"
}

get_grafana_url() {
    log_info "Grafana URLs:"
    
    # NodePort
    local nodeport=$(kubectl get svc grafana -n "$NAMESPACE" -o jsonpath='{.spec.ports[0].nodePort}')
    echo "  NodePort:    http://<NODE_IP>:$nodeport"
    
    # Minikube
    if command -v minikube &> /dev/null; then
        local minikube_ip=$(minikube ip 2>/dev/null || echo "N/A")
        if [ "$minikube_ip" != "N/A" ]; then
            echo "  Minikube:    http://$minikube_ip:$nodeport"
        fi
    fi
    
    echo "  Port-forward: kubectl port-forward svc/grafana -n $NAMESPACE 3000:3000"
    echo "               http://127.0.0.1:3000"
    echo ""
    echo "  Login credentials:"
    echo "    Username: admin"
    echo "    Password: admin123456789"
}

setup_port_forwards() {
    log_info "Setting up port-forwards..."
    
    # Check if port-forward processes already exist
    if lsof -Pi :9090 -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warn "Port 9090 already in use (Prometheus)"
    else
        log_info "Setting up Prometheus port-forward on 9090..."
        kubectl port-forward svc/prometheus -n "$NAMESPACE" 9090:9090 &
    fi
    
    if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warn "Port 3000 already in use (Grafana)"
    else
        log_info "Setting up Grafana port-forward on 3000..."
        kubectl port-forward svc/grafana -n "$NAMESPACE" 3000:3000 &
    fi
    
    sleep 2
    log_success "Port-forwards configured"
}

check_targets() {
    log_info "Checking Prometheus scrape targets..."
    
    # Wait for Prometheus to be ready
    local max_tries=30
    local tries=0
    while [ $tries -lt $max_tries ]; do
        if curl -s http://127.0.0.1:9090/api/v1/targets &> /dev/null; then
            break
        fi
        tries=$((tries + 1))
        sleep 1
    done
    
    if [ $tries -eq $max_tries ]; then
        log_warn "Could not connect to Prometheus. Ensure port-forward is active."
        return
    fi
    
    echo ""
    echo "Active Targets:"
    curl -s http://127.0.0.1:9090/api/v1/targets | jq -r '.data.activeTargets[] | "\(.labels.job) (\(.health))"' 2>/dev/null || true
    echo ""
}

check_status() {
    log_info "Checking monitoring stack status..."
    
    echo ""
    log_info "Deployments:"
    kubectl get deployment -n "$NAMESPACE" -l app=prometheus,app.kubernetes.io/name=prometheus -o wide || true
    kubectl get deployment -n "$NAMESPACE" -l app=grafana,app.kubernetes.io/name=grafana -o wide || true
    
    echo ""
    log_info "Pods:"
    kubectl get pods -n "$NAMESPACE" -l app=prometheus -o wide || true
    kubectl get pods -n "$NAMESPACE" -l app=grafana -o wide || true
    
    echo ""
    log_info "Services:"
    kubectl get svc -n "$NAMESPACE" -l app=prometheus,app=grafana -o wide || true
    
    echo ""
}

view_logs() {
    local component=${1:-prometheus}
    log_info "Viewing logs for $component..."
    kubectl logs -f "deployment/$component" -n "$NAMESPACE" --tail=100
}

cleanup() {
    log_warn "Removing monitoring stack..."
    kubectl delete -f "$PROJECT_ROOT/$MONITORING_DIR/prometheus-grafana-deployment.yaml" --ignore-not-found=true
    kubectl delete -f "$PROJECT_ROOT/$MONITORING_DIR/prometheus-config.yaml" --ignore-not-found=true
    log_success "Monitoring stack removed"
}

open_browser() {
    local service=${1:-prometheus}
    local port=${2:-9090}
    
    if command -v minikube &> /dev/null; then
        log_info "Opening $service in browser via Minikube..."
        minikube service "$service" -n "$NAMESPACE" &
    else
        log_warn "Minikube not found. Please manually open http://127.0.0.1:$port in your browser"
        log_info "First ensure port-forward is running:"
        log_info "  kubectl port-forward svc/$service -n $NAMESPACE $port:$port"
    fi
}

# Show usage
usage() {
    cat << EOF
${BLUE}Monitoring Stack Management Script${NC}

Usage: $0 [command] [options]

Commands:
  deploy              Deploy monitoring stack (Prometheus + Grafana)
  status              Show status of monitoring components
  logs [component]    View logs (default: prometheus)
  prometheus-url      Show Prometheus URLs
  grafana-url         Show Grafana URLs
  port-forward        Setup port-forwards for local access
  check-targets       Check Prometheus scrape targets
  open-prometheus     Open Prometheus in browser
  open-grafana        Open Grafana in browser
  cleanup             Remove monitoring stack
  help                Show this help message

Examples:
  # Deploy monitoring stack
  $0 deploy

  # Check status
  $0 status

  # View Prometheus logs
  $0 logs prometheus

  # Setup port-forwards and show URLs
  $0 port-forward
  $0 prometheus-url
  $0 grafana-url

  # Check if targets are being scraped
  $0 check-targets

  # Remove monitoring stack
  $0 cleanup

Environment Variables:
  NAMESPACE            Kubernetes namespace (default: mlflow-prod)
  MONITORING_DIR       Monitoring resources directory (default: k8s/monitoring)

EOF
}

# Main
main() {
    local command="${1:-help}"
    
    case "$command" in
        deploy)
            check_prerequisites
            deploy_monitoring
            verify_deployment
            echo ""
            get_prometheus_url
            echo ""
            get_grafana_url
            echo ""
            log_info "To access services, run:"
            log_info "  $0 port-forward"
            ;;
        status)
            check_status
            ;;
        logs)
            view_logs "${2:-prometheus}"
            ;;
        prometheus-url)
            get_prometheus_url
            ;;
        grafana-url)
            get_grafana_url
            ;;
        port-forward)
            setup_port_forwards
            echo ""
            get_prometheus_url
            echo ""
            get_grafana_url
            ;;
        check-targets)
            check_targets
            ;;
        open-prometheus)
            setup_port_forwards
            open_browser "prometheus" 9090
            ;;
        open-grafana)
            setup_port_forwards
            open_browser "grafana" 3000
            ;;
        cleanup)
            cleanup
            ;;
        help)
            usage
            ;;
        *)
            log_error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

main "$@"
