# Monitoring & Observability Implementation Summary

## 📋 Overview

Complete monitoring and observability stack has been implemented for the end-to-end MLflow project using **Prometheus** and **Grafana**. This enables real-time metrics collection, visualization, and alerting for both MLflow server and model serving infrastructure.

---

## 📁 Directory Structure

```
project-root/
├── k8s/
│   └── monitoring/                                  # All monitoring resources
│       ├── prometheus-config.yaml                  # Prometheus scrape config + alert rules
│       ├── prometheus-grafana-deployment.yaml      # Prometheus & Grafana K8s manifests
│       └── dashboards/
│           └── mlflow-monitoring-dashboard.json    # Pre-built Grafana dashboard
│
├── monitoring/
│   └── README.md                                   # Comprehensive monitoring guide (EN/PT-BR)
│
├── scripts/
│   └── monitoring.sh                               # Automation script for monitoring deployment
│
├── README.md                                       # Updated main README (new monitoring section)
│
└── notebooks/step-by-step_instructions_for_execution.ipynb   # Updated notebook (new Step 8 - Monitoring)
```

---

## 🚀 Quick Start

### 1. Deploy Monitoring Stack

**Option A - Using automation script (recommended):**
```bash
# Make script executable
chmod +x scripts/monitoring.sh

# Deploy monitoring stack
./scripts/monitoring.sh deploy

# Setup port-forwards and show URLs
./scripts/monitoring.sh port-forward
```

**Option B - Manual kubectl deployment:**
```bash
# Deploy Prometheus config and alert rules
kubectl apply -f k8s/monitoring/prometheus-config.yaml

# Deploy Prometheus and Grafana services
kubectl apply -f k8s/monitoring/prometheus-grafana-deployment.yaml

# Verify deployments
kubectl get all -n mlflow-prod
```

### 2. Access Prometheus

```bash
# Port-forward to local machine
kubectl port-forward svc/prometheus -n mlflow-prod 9090:9090

# Open in browser
open http://127.0.0.1:9090
# Or: curl -s http://127.0.0.1:9090/-/healthy
```

### 3. Access Grafana

```bash
# Port-forward to local machine
kubectl port-forward svc/grafana -n mlflow-prod 3000:3000

# Open in browser
open http://127.0.0.1:3000
# Or: curl -s http://127.0.0.1:3000/api/health

# Default credentials
# Username: admin
# Password: admin123456789
```

### 4. Verify Monitoring

```bash
# Check Prometheus targets
./scripts/monitoring.sh check-targets

# View component status
./scripts/monitoring.sh status

# View logs
./scripts/monitoring.sh logs prometheus
./scripts/monitoring.sh logs grafana
```

---

## 📊 Components Deployed

### Prometheus

**Configuration File:** `k8s/monitoring/prometheus-config.yaml`

**Manifest File:** `k8s/monitoring/prometheus-grafana-deployment.yaml`

**Features:**
- Service account with RBAC permissions for Kubernetes API access
- Deployment: 1 replica (can be increased for HA)
- Storage: 30-day metrics retention (emptyDir)
- NodePort Service: Port 30090 for external access
- Health checks: liveness + readiness probes

**Scrape Targets:**
| Target | Job | Interval | Metrics Path |
|--------|-----|----------|--------------|
| Prometheus | prometheus | 15s | - |
| MLflow Server | mlflow-server | 10s | `/metrics` |
| Model Server | model-server | 10s | `/metrics` |
| Kubernetes API | kubernetes-apiservers | - | - |
| Node Metrics | kubernetes-nodes | - | - |
| Pod Metrics | kubernetes-pods | - | - |

**Alert Rules:** 
- `MLflowServerDown` - Server unreachable (1m threshold)
- `ModelServerDown` - Model server unreachable (1m threshold)
- `HighCPUUsage` - CPU > 80% (5m threshold)
- `HighMemoryUsage` - Memory > 85% (5m threshold)
- `PodCrashLooping` - Pod restarting frequently (5m threshold)
- `HighModelLatency` - p95 latency > 1 second
- `MLflowExperimentFailure` - Training run failed

### Grafana

**Manifest File:** `k8s/monitoring/prometheus-grafana-deployment.yaml`

**Features:**
- Deployment: 1 replica
- Pre-configured datasource: Prometheus (http://prometheus:9090)
- Dashboard provisioning support via ConfigMap
- Storage: emptyDir (dashboards persist for pod lifetime)
- NodePort Service: Port 30300 for external access
- Health checks: liveness + readiness probes
- Security: Non-root user (472), read-only plugins mount

**Pre-built Dashboards:**
- **MLflow & Model Server Monitoring**: Request metrics, latency, error rates

**Grafana Plugins:**
- Pie Chart plugin (installed)

### Dashboards

**File:** `k8s/monitoring/dashboards/mlflow-monitoring-dashboard.json`

**Panels:**
1. **MLflow Server Status** - Real-time server health indicator
2. **Model Server Status** - Real-time model server health
3. **MLflow Request Latency (p95, p99)** - Request performance over time
4. **Model Server Request Rate** - Throughput by method/path
5. **MLflow Error Rate (4xx, 5xx)** - Error tracking
6. **Model Server Error Rate (4xx, 5xx)** - Error tracking

---

## 🔧 Management Commands

### Using Automation Script

```bash
# Deploy monitoring stack
./scripts/monitoring.sh deploy

# Check status of all components
./scripts/monitoring.sh status

# View logs
./scripts/monitoring.sh logs prometheus    # Prometheus logs
./scripts/monitoring.sh logs grafana       # Grafana logs

# Show access URLs
./scripts/monitoring.sh prometheus-url     # Prometheus URLs
./scripts/monitoring.sh grafana-url        # Grafana URLs

# Setup port-forwards for local access
./scripts/monitoring.sh port-forward

# Check Prometheus scrape targets
./scripts/monitoring.sh check-targets

# Open in browser (requires Minikube)
./scripts/monitoring.sh open-prometheus
./scripts/monitoring.sh open-grafana

# Remove monitoring stack
./scripts/monitoring.sh cleanup

# Show help
./scripts/monitoring.sh help
```

### Manual kubectl Commands

```bash
# Check all monitoring resources
kubectl get all -n mlflow-prod

# Check only monitoring components
kubectl get pods -n mlflow-prod -l app=prometheus,app=grafana
kubectl get svc -n mlflow-prod -l app=prometheus,app=grafana
kubectl get deployment -n mlflow-prod -l app=prometheus,app=grafana

# View Prometheus configuration
kubectl get configmap prometheus-config -n mlflow-prod -o yaml

# View Prometheus alert rules
kubectl get configmap prometheus-rules -n mlflow-prod -o yaml

# View Grafana datasource configuration
kubectl get configmap grafana-datasources -n mlflow-prod -o yaml

# View logs
kubectl logs -f deployment/prometheus -n mlflow-prod --tail=100
kubectl logs -f deployment/grafana -n mlflow-prod --tail=100

# Restart components (rolling update)
kubectl rollout restart deployment/prometheus -n mlflow-prod
kubectl rollout restart deployment/grafana -n mlflow-prod

# Check resource usage
kubectl top pods -n mlflow-prod
kubectl top nodes

# Port-forward
kubectl port-forward svc/prometheus -n mlflow-prod 9090:9090 &
kubectl port-forward svc/grafana -n mlflow-prod 3000:3000 &
```

---

## 📈 Key Metrics to Monitor

### MLflow Server Metrics

```promql
# Request success rate (%)
sum(rate(http_requests_total{job="mlflow-server",status="200"}[5m])) / 
sum(rate(http_requests_total{job="mlflow-server"}[5m])) * 100

# Request latency (p95)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="mlflow-server"}[5m]))

# Error rate (4xx, 5xx per second)
sum(rate(http_requests_total{job="mlflow-server",status=~"4..|5.."}[5m])) by (status)

# Total runs by status
sum(increase(mlflow_runs_finished_total[1h])) by (status)

# Experiments count
mlflow_experiment_created_total
```

### Model Server Metrics

```promql
# Inference requests per second
sum(rate(http_requests_total{job="model-server",path="/invocations"}[5m])) by (status)

# Inference latency (p95, p99)
histogram_quantile(0.95, rate(mlflow_model_request_duration_seconds_bucket[5m]))

# Predictions per second
rate(mlflow_predictions_total[5m])

# Model server error rate
sum(rate(http_requests_total{job="model-server",status=~"4..|5.."}[5m]))
```

### System Metrics

```promql
# Container CPU usage
rate(container_cpu_usage_seconds_total{namespace="mlflow-prod"}[5m])

# Container memory usage
container_memory_usage_bytes{namespace="mlflow-prod"}

# Node CPU usage
rate(node_cpu_seconds_total{mode!="idle"}[5m])

# Pod count
count(kube_pod_info{namespace="mlflow-prod"})
```

---

## 🔍 Troubleshooting

### Prometheus Targets Not Scraping

```bash
# Check Prometheus logs
kubectl logs deployment/prometheus -n mlflow-prod

# Verify service discovery
curl -s http://127.0.0.1:9090/service-discovery

# Test connectivity to MLflow server
kubectl exec -it deployment/prometheus -n mlflow-prod -- \
  curl -v http://mlflow-service.mlflow-prod.svc.cluster.local:5000/metrics
```

### Grafana Cannot Connect to Prometheus

```bash
# Verify Grafana can reach Prometheus
kubectl exec -it deployment/grafana -n mlflow-prod -- \
  curl -v http://prometheus:9090/-/healthy

# Check Grafana datasource configuration
# In Grafana UI: Configuration → Data Sources → Prometheus → Test
```

### High Memory Usage

```bash
# Reduce cardinality by dropping high-cardinality metrics
# Edit prometheus-config.yaml and add metric_relabel_configs

# Reduce scrape interval (less frequent scraping)
# Change scrape_interval from 15s to 30s or 60s

# Increase Prometheus resource limits
# Edit prometheus-grafana-deployment.yaml
```

### Port Already in Use

```bash
# Kill existing port-forward processes
killall kubectl

# Or find and kill specific process
lsof -i :9090
kill -9 <PID>

# Or use different ports
kubectl port-forward svc/prometheus -n mlflow-prod 9099:9090
```

---

## 📚 Documentation Files

### Main Files

| File | Purpose |
|------|---------|
| `monitoring/README.md` | Comprehensive guide (EN/PT-BR) |
| `k8s/monitoring/prometheus-config.yaml` | Prometheus config + alert rules |
| `k8s/monitoring/prometheus-grafana-deployment.yaml` | K8s manifests |
| `k8s/monitoring/dashboards/mlflow-monitoring-dashboard.json` | Pre-built dashboard |
| `scripts/monitoring.sh` | Automation script |
| `README.md` | Main README with monitoring section |
| `notebooks/step-by-step_instructions_for_execution.ipynb` | Notebook Step 8 - Monitoring |

### Referenced from These Files

- **monitoring/README.md**: 
  - Complete architecture overview
  - Detailed setup instructions for Kubernetes
  - PromQL query examples
  - Dashboard creation guide
  - Alert configuration
  - Performance tuning
  - Troubleshooting (EN/PT-BR)

- **README.md** (main):
  - Quick start section
  - Link to monitoring guide
  - Key features summary
  - Component overview table

- **notebooks/step-by-step_instructions_for_execution.ipynb** (Step 8):
  - Deploy monitoring stack
  - Access Prometheus and Grafana
  - View pre-built dashboard
  - Create custom dashboards
  - View alert rules
  - Performance tuning
  - Troubleshooting

---

## 🎯 Next Steps

### 1. Deploy (if not already done)

```bash
./scripts/monitoring.sh deploy
```

### 2. Access Services

```bash
./scripts/monitoring.sh port-forward
```

### 3. Verify Targets

```bash
./scripts/monitoring.sh check-targets
```

### 4. View Dashboards

1. Open Grafana: http://127.0.0.1:3000
2. Login with `admin` / `admin123456789`
3. Navigate to **Dashboards** → **MLflow & Model Server Monitoring**

### 5. Create Custom Dashboards

1. In Grafana: **+** → **Dashboard** → **New Dashboard**
2. Add panels with PromQL queries
3. Reference examples in `monitoring/README.md`

### 6. Configure Alerts

1. In Grafana: **Alerting** → **Alert Rules**
2. Review pre-configured alerts
3. Add notification channels (Email, Slack, PagerDuty, etc.)

### 7. Monitor Production

- Set refresh rate: 10s or 30s
- Create dashboards for key metrics
- Configure alerts for critical thresholds
- Implement alerting integration (Slack, PagerDuty)

---

## 📝 Configuration Reference

### Prometheus Retention

**Default:** 30 days

**Change retention:**
```bash
kubectl patch deployment prometheus -n mlflow-prod -p \
  '{"spec":{"template":{"spec":{"containers":[{"name":"prometheus","args":["--storage.tsdb.retention.time=365d"]}]}}}}'
```

### Grafana Admin Password

**Current:** `admin123456789` (base64 encoded in Secret)

**Change password:**
```bash
# Generate new base64 encoded password
echo -n "newpassword" | base64

# Update secret
kubectl patch secret grafana-secret -n mlflow-prod -p \
  '{"data":{"admin-password":"bmV3cGFzc3dvcmQ="}}'

# Restart Grafana pod
kubectl rollout restart deployment/grafana -n mlflow-prod
```

### Scrape Interval

**Default:** 15s (global), 10s (MLflow/model servers)

**Change interval (edit prometheus-config.yaml):**
```yaml
global:
  scrape_interval: 30s  # Change from 15s
```

Then re-apply:
```bash
kubectl apply -f k8s/monitoring/prometheus-config.yaml
```

---

## 🔗 External Links

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Kubernetes Metrics](https://kubernetes.io/docs/tasks/debug-application-cluster/resource-metrics-pipeline/)
- [PromQL Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Kubernetes Monitoring Best Practices](https://kubernetes.io/docs/tasks/run-application/monitor-application/)

---

## ✅ Implementation Checklist

- ✅ Prometheus configuration with scrape targets
- ✅ Prometheus alert rules (6 critical/warning alerts)
- ✅ Kubernetes manifests (RBAC, ServiceAccount, Deployment, Service)
- ✅ Grafana deployment with Prometheus datasource
- ✅ Pre-built dashboard (6 panels)
- ✅ Dashboard provisioning via ConfigMap
- ✅ Comprehensive documentation (EN/PT-BR)
- ✅ Automation script for easy deployment
- ✅ README section with quick start
- ✅ Notebook section with step-by-step guide
- ✅ Health checks (liveness + readiness probes)
- ✅ Resource requests/limits
- ✅ Security context (non-root users)

---

## 📞 Support

For detailed help, refer to:
1. **[monitoring/README.md](../monitoring/README.md)** - Comprehensive guide
2. **[README.md#monitoring-observability](../README.md#-monitoring--observability)** - Quick reference
3. **Notebook Step 8** - Interactive walkthrough
4. **scripts/monitoring.sh help** - Command reference

---

**Last Updated:** February 19, 2026  
**Project:** End-to-End MLflow Project  
**Status:** ✅ Complete & Ready for Production
