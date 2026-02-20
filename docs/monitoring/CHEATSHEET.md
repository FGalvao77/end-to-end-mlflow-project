# Monitoring Quick Reference Guide / Guia Rápido de Referência

## 🚀 Deploy (Implantação)

```bash
# Deploy monitoring stack
./scripts/monitoring.sh deploy

# Or manually
kubectl apply -f k8s/monitoring/prometheus-config.yaml
kubectl apply -f k8s/monitoring/prometheus-grafana-deployment.yaml
```

---

## 🌐 Access URLs (URLs de Acesso)

```bash
# Show all URLs
./scripts/monitoring.sh prometheus-url
./scripts/monitoring.sh grafana-url

# Setup port-forwards
./scripts/monitoring.sh port-forward

# Then open in browser
http://127.0.0.1:9090    # Prometheus
http://127.0.0.1:3000    # Grafana (admin / admin123456789)
```

---

## 📊 Prometheus Queries (PromQL)

### Health & Status
```promql
up{job="mlflow-server"}              # MLflow server status (1=up, 0=down)
up{job="model-server"}               # Model server status
up{job="prometheus"}                 # Prometheus status
```

### MLflow Server Metrics
```promql
# Request rate (requests per second)
sum(rate(http_requests_total{job="mlflow-server"}[5m])) by (path)

# Success rate (%)
sum(rate(http_requests_total{job="mlflow-server",status="200"}[5m])) / 
sum(rate(http_requests_total{job="mlflow-server"}[5m])) * 100

# Error rate
sum(rate(http_requests_total{job="mlflow-server",status=~"4..|5.."}[5m])) by (status)

# Request latency (p95)
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="mlflow-server"}[5m]))

# Request latency (p99)
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{job="mlflow-server"}[5m]))

# Runs created
sum(increase(mlflow_runs_created_total[1h]))

# Runs failed
sum(increase(mlflow_runs_finished_total{status="FAILED"}[1h]))

# Experiments count
mlflow_experiment_created_total
```

### Model Server Metrics
```promql
# Inference request rate
sum(rate(http_requests_total{job="model-server",path="/invocations"}[5m])) by (status)

# Inference latency (p95)
histogram_quantile(0.95, rate(mlflow_model_request_duration_seconds_bucket[5m]))

# Predictions per second
rate(mlflow_predictions_total[5m])

# Error rate
sum(rate(http_requests_total{job="model-server",status=~"4..|5.."}[5m])) by (status)

# Success rate (%)
sum(rate(http_requests_total{job="model-server",status="200"}[5m])) / 
sum(rate(http_requests_total{job="model-server"}[5m])) * 100
```

### System Metrics
```promql
# CPU usage by pod
rate(container_cpu_usage_seconds_total{namespace="mlflow-prod"}[5m])

# Memory usage by pod
container_memory_usage_bytes{namespace="mlflow-prod"}

# Load average
node_load1

# Working set memory
container_working_set_memory_bytes{namespace="mlflow-prod"}

# Pod restart count
increase(kube_pod_container_status_restarts_total{namespace="mlflow-prod"}[1h])
```

---

## 🔧 Common Commands (Comandos Comuns)

### Check Status
```bash
./scripts/monitoring.sh status
kubectl get all -n mlflow-prod
kubectl get pods -n mlflow-prod -l app=prometheus,app=grafana
```

### View Logs
```bash
./scripts/monitoring.sh logs prometheus
./scripts/monitoring.sh logs grafana

# Or manually
kubectl logs -f deployment/prometheus -n mlflow-prod --tail=100
kubectl logs -f deployment/grafana -n mlflow-prod --tail=100
```

### Check Targets
```bash
./scripts/monitoring.sh check-targets

# Or directly
curl -s http://127.0.0.1:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, status: .health}'
```

### Restart Components
```bash
kubectl rollout restart deployment/prometheus -n mlflow-prod
kubectl rollout restart deployment/grafana -n mlflow-prod
```

### Port-Forward
```bash
# Prometheus
kubectl port-forward svc/prometheus -n mlflow-prod 9090:9090

# Grafana
kubectl port-forward svc/grafana -n mlflow-prod 3000:3000

# Both (background)
./scripts/monitoring.sh port-forward
```

### Delete/Cleanup
```bash
./scripts/monitoring.sh cleanup

# Or manually
kubectl delete namespace mlflow-prod
```

---

## 📈 Grafana Dashboards

### Built-in Dashboard
- **MLflow & Model Server Monitoring**
  - MLflow Server Status
  - Model Server Status
  - MLflow Request Latency
  - Model Server Request Rate
  - MLflow Error Rate
  - Model Server Error Rate

### Import Dashboard
1. Grafana UI → **+** → **Import**
2. Upload `k8s/monitoring/dashboards/mlflow-monitoring-dashboard.json`
3. Select Prometheus as datasource

### Create Custom Dashboard
1. Grafana UI → **+** → **Dashboard** → **New Dashboard**
2. **Add Panel** → Select queries from above
3. Configure visualization and save

---

## 🚨 Alert Rules (Regras de Alerta)

### Pre-configured Alerts
```
MLflowServerDown         - MLflow server unreachable (1 min)
ModelServerDown          - Model server unreachable (1 min)
HighCPUUsage             - CPU > 80% (5 min)
HighMemoryUsage          - Memory > 85% (5 min)
PodCrashLooping          - Pod restarting frequently (5 min)
HighModelLatency         - p95 latency > 1 sec
MLflowExperimentFailure  - Training run failed
```

### View Alerts
```bash
# In Prometheus
curl -s http://127.0.0.1:9090/api/v1/alerts | jq '.data[] | {alert: .labels.alertname, status: .state}'

# In Grafana
UI → Alerting → Alert rules
```

### Configure Notifications (Grafana)
1. Grafana UI → **Alerting** → **Contact points**
2. Click **New contact point**
3. Choose type: Email, Slack, PagerDuty, Webhook, etc.
4. Fill in details and test

---

## 🔍 Troubleshooting Quick Fixes

### Prometheus Not Scraping Targets
```bash
# Check logs
kubectl logs deployment/prometheus -n mlflow-prod | grep error

# Verify service discovery
curl -s http://127.0.0.1:9090/service-discovery | jq '.[]'

# Test target connectivity
kubectl exec -it pod/prometheus-xxx -n mlflow-prod -- \
  curl -v http://mlflow-service.mlflow-prod.svc.cluster.local:5000/metrics
```

### Grafana Dashboard Not Loading
```bash
# Check Grafana logs
kubectl logs deployment/grafana -n mlflow-prod | grep error

# Verify datasource
curl -s http://127.0.0.1:3000/api/datasources | jq '.[] | {name: .name, type: .type}'

# Test Prometheus connectivity
kubectl exec -it pod/grafana-xxx -n mlflow-prod -- \
  curl -v http://prometheus:9090/-/healthy
```

### High Memory/CPU
```bash
# Check resource usage
kubectl top pods -n mlflow-prod
kubectl top nodes

# Reduce scrape interval
# Edit k8s/monitoring/prometheus-config.yaml:
# scrape_interval: 30s  # Change from 15s or 10s

# Command to apply
kubectl apply -f k8s/monitoring/prometheus-config.yaml
```

### Port Already in Use
```bash
# Find process using port
lsof -i :9090
lsof -i :3000

# Kill it
kill -9 <PID>

# Or use different ports
kubectl port-forward svc/prometheus -n mlflow-prod 9099:9090
kubectl port-forward svc/grafana -n mlflow-prod 3001:3000
```

---

## 📚 Documentation Links

| Document | Purpose |
|----------|---------|
| `monitoring/README.md` | Complete guide (EN/PT-BR) |
| `monitoring/IMPLEMENTATION_SUMMARY.md` | This summary |
| `monitoring/CHEATSHEET.md` | Quick reference (this file) |
| `k8s/monitoring/prometheus-config.yaml` | Prometheus configuration |
| `k8s/monitoring/prometheus-grafana-deployment.yaml` | K8s manifests |
| `README.md` | Main project README |
| `notebooks/step-by-step_instructions_for_execution.ipynb` | Step 8 - Monitoring |

---

## 🎯 Common Workflows

### Daily Operations
```bash
# Check status
./scripts/monitoring.sh status

# View Prometheus targets
./scripts/monitoring.sh check-targets

# View Grafana dashboard
# Open http://127.0.0.1:3000 (after port-forward)

# Check logs
./scripts/monitoring.sh logs prometheus
./scripts/monitoring.sh logs grafana
```

### Alert Response
```bash
# View active alerts
curl -s http://127.0.0.1:9090/api/v1/alerts | jq '.data[] | select(.state=="firing")'

# View alert in Grafana
# UI → Alerting → Alert rules → Click alert name

# Investigate
# View logs: ./scripts/monitoring.sh logs <component>
# Check metrics in Prometheus/Grafana
# Scale or restart pods if needed
```

### Performance Investigation
```bash
# Query key metrics in Prometheus
# 1. http_requests_total - request volume
# 2. http_request_duration_seconds - latency
# 3. container_cpu_usage_seconds_total - CPU usage
# 4. container_memory_usage_bytes - memory usage

# Create dashboard panel with query
# In Grafana: + → Dashboard → + Panel → Add query

# Use time range selector to zoom in on issue
# Check logs during that time: kubectl logs --since 5m
```

### Capacity Planning
```bash
# Monitor trends over time
# In Grafana, change time range to 7d, 30d, 90d

# Query growth rates
# rate(http_requests_total[1d])
# increase(http_requests_total[7d])

# Check resource usage trends
# container_memory_usage_bytes over time
# rate(container_cpu_usage_seconds_total[5m]) trends

# Plan capacity based on trends
```

---

## ⚡ Performance Tips

### Reduce Data Collection (Lower CPU/Memory)
```bash
# Increase scrape interval
scrape_interval: 60s  # From 15s

# Drop high-cardinality metrics
metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'node_netdev.*'
    action: drop
```

### Archive Old Data (Lower Disk Usage)
```bash
# Decrease retention
--storage.tsdb.retention.time=7d  # From 30d

# Or use compression
--storage.tsdb.max-block-duration=2h
```

### Optimize Queries (Faster Dashboards)
```promql
# Use recording rules (in alert rules file)
groups:
  - name: custom_rules
    rules:
      - record: job:requests_per_second:5m
        expr: sum(rate(http_requests_total[5m])) by (job)

# Then use in Grafana
job:requests_per_second:5m{job="mlflow-server"}
```

---

## 🔐 Security Notes

- Default Grafana password should be changed in production
- Prometheus is not password-protected (firewall it behind ingress)
- Use NetworkPolicy to restrict traffic
- Store secrets in Kubernetes Secrets (not ConfigMaps)
- Enable HTTPS/TLS for production
- Regular backup of dashboards and alert rules

---

## 📞 Quick Help

```bash
# List all available commands
./scripts/monitoring.sh help

# Detailed documentation
head -100 monitoring/README.md

# Examples
grep -r "promql\|PromQL" monitoring/
```

---

**Last Updated:** February 19, 2026  
**Status:** ✅ Ready for Production Use
