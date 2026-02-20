# 📊 Monitoring Stack - Complete File Structure & Navigation Guide

## 📁 Directory Overview

```
project-root/
│
├── 📂 k8s/
│   ├── mlflow-deployment.yaml          # Main MLflow & model server deployment
│   ├── README.md                       # Kubernetes guide
│   │
│   └── 📂 monitoring/                  ⭐ ALL MONITORING FILES HERE
│       ├── prometheus-config.yaml      # ← Prometheus configuration + alert rules
│       ├── prometheus-grafana-deployment.yaml  # ← K8s manifests (deployment, service, RBAC)
│       │
│       └── 📂 dashboards/
│           └── mlflow-monitoring-dashboard.json  # ← Pre-built Grafana dashboard
│
├── 📂 monitoring/                      ⭐ MONITORING DOCUMENTATION
│   ├── README.md                       # ← MAIN GUIDE (comprehensive, EN/PT-BR)
│   ├── IMPLEMENTATION_SUMMARY.md       # ← Quick implementation reference
│   ├── CHEATSHEET.md                   # ← Quick command reference
│   └── INDEX.md                        # ← This file - navigation guide
│
├── 📂 scripts/
│   ├── run.sh                          # Docker orchestration script
│   ├── monitoring.sh                   # ← Monitoring automation script
│   └── README.md
│
├── README.md                           # ← Main project README (has monitoring section)
├── notebooks/step-by-step_instructions_for_execution.ipynb  # ← Notebook (Step 8 - Monitoring)
└── [other project files...]
```

---

## 🗺️ Navigation Guide: Where to Find What

### 🚀 **I want to DEPLOY monitoring**

**Start Here:** [`scripts/monitoring.sh`](../scripts/monitoring.sh)

```bash
./scripts/monitoring.sh deploy
```

Or read: [`monitoring/README.md`](./README.md) → **Quick Start** section

---

### 📖 **I want to LEARN about the implementation**

**Read in order:**
1. [`README.md` (main)](../README.md) → Monitoring & Observability section
2. [`monitoring/README.md`](./README.md) → Complete guide
3. [`notebooks/step-by-step_instructions_for_execution.ipynb`](../notebooks/step-by-step_instructions_for_execution.ipynb) → Step 8

---

### 📊 **I want to ACCESS grafana/prometheus**

**Read:** [`monitoring/CHEATSHEET.md`](./CHEATSHEET.md) → Access URLs section

Or run:
```bash
./scripts/monitoring.sh port-forward
./scripts/monitoring.sh prometheus-url
./scripts/monitoring.sh grafana-url
```

---

### 📈 **I want to WRITE PROMQL QUERIES**

**Read:** 
1. [`monitoring/README.md`](./README.md) → Key Metrics section
2. [`monitoring/CHEATSHEET.md`](./CHEATSHEET.md) → Prometheus Queries section
3. [`monitoring/README.md`](./README.md) → Creating Custom Dashboards section

---

### ⚙️ **I want to CONFIGURE/CUSTOMIZE monitoring**

**Files to edit:**

| Task | File | Section |
|------|------|---------|
| Scrape targets, intervals | `k8s/monitoring/prometheus-config.yaml` | `scrape_configs` |
| Alert rules | `k8s/monitoring/prometheus-config.yaml` | `rule_files` |
| Grafana dashboard | `k8s/monitoring/dashboards/*.json` | Edit in Grafana UI |
| K8s resources | `k8s/monitoring/prometheus-grafana-deployment.yaml` | Entire file |
| Resource limits | `k8s/monitoring/prometheus-grafana-deployment.yaml` | `resources` section |

---

### 🔧 **I want to TROUBLESHOOT issues**

**Read:** [`monitoring/README.md`](./README.md) → Troubleshooting section

Or run:
```bash
./scripts/monitoring.sh logs prometheus
./scripts/monitoring.sh logs grafana
./scripts/monitoring.sh check-targets
./scripts/monitoring.sh status
```

---

### 💾 **I want to BACKUP/RESTORE dashboards**

```bash
# Export dashboard from Grafana UI:
# Grafana → Dashboard → Share → Export JSON

# Save to version control:
cp exported-dashboard.json k8s/monitoring/dashboards/

# Commit to git:
git add k8s/monitoring/dashboards/
git commit -m "Update dashboard"

# Restore/apply:
kubectl create configmap grafana-dashboards \
  --from-file=k8s/monitoring/dashboards/ -n mlflow-prod
kubectl rollout restart deployment/grafana -n mlflow-prod
```

---

### 📊 **I want to CREATE A NEW DASHBOARD**

**Option A - Via Grafana UI (recommended):**
1. Grafana → + → Dashboard → New Dashboard
2. Add panels using PromQL queries from [`monitoring/CHEATSHEET.md`](./CHEATSHEET.md)
3. Export JSON (Grafana → Dashboard → Share → Export JSON)
4. Save to `k8s/monitoring/dashboards/`

**Option B - Edit JSON directly:**
1. Copy `k8s/monitoring/dashboards/mlflow-monitoring-dashboard.json`
2. Edit JSON (structure: panels, datasources, etc.)
3. Import to Grafana via UI → Import

---

### 🚨 **I want to CONFIGURE ALERTS**

**Location:** `k8s/monitoring/prometheus-config.yaml` → `rule_files` section

**Steps:**
1. Edit `prometheus-config.yaml`
2. Add alert rule to `prometheus-rules` ConfigMap
3. Apply: `kubectl apply -f k8s/monitoring/prometheus-config.yaml`
4. Configure notification channels in Grafana UI

---

### 📝 **I want to READ DETAILED DOCUMENTATION**

| Document | Best For |
|----------|----------|
| [`README.md`](./README.md) | Complete guide, concepts, best practices |
| [`IMPLEMENTATION_SUMMARY.md`](./IMPLEMENTATION_SUMMARY.md) | Quick reference, what's deployed |
| [`CHEATSHEET.md`](./CHEATSHEET.md) | Fast lookups, common commands |
| `k8s/monitoring/prometheus-config.yaml` | Understanding Prometheus config |
| `k8s/monitoring/prometheus-grafana-deployment.yaml` | Understanding K8s manifests |
| `../notebooks/step-by-step_instructions_for_execution.ipynb` | Interactive walkthrough (Step 8) |

---

## 📚 Complete File Reference

### Configuration Files (Kubernetes)

#### **`k8s/monitoring/prometheus-config.yaml`**
```yaml
ConfigMap: prometheus-config
├── prometheus.yml
│   ├── global (scrape_interval, evaluation_interval)
│   ├── alerting (alertmanagers)
│   ├── rule_files (alert rules location)
│   └── scrape_configs
│       ├── prometheus
│       ├── mlflow-server
│       ├── model-server
│       ├── kubernetes-apiservers
│       ├── kubernetes-nodes
│       ├── kubernetes-pods
│       └── kube-state-metrics
│
ConfigMap: prometheus-rules
└── alert_rules.yml
    ├── mlflow_alerts
    │   ├── MLflowServerDown
    │   ├── ModelServerDown
    │   ├── HighCPUUsage
    │   └── HighMemoryUsage
    └── mlflow_training_alerts
        ├── MLflowExperimentFailure
        └── HighModelLatency
```

#### **`k8s/monitoring/prometheus-grafana-deployment.yaml`**
```yaml
ServiceAccount: prometheus (for RBAC)
ClusterRole: prometheus (Kubernetes API access)
ClusterRoleBinding: prometheus (bind role to SA)

Deployment: prometheus
├── replica: 1
├── image: prom/prometheus:v2.50.0
├── ports: 9090 (web)
├── volumeMounts:
│   ├── prometheus-config
│   ├── prometheus-rules
│   └── prometheus-storage (emptyDir)
└── resources:
    ├── requests: 100m CPU, 256Mi mem
    └── limits: 500m CPU, 1Gi mem

Service: prometheus (NodePort 30090)

ConfigMap: grafana-datasources
└── prometheus.yaml (datasource config)

Deployment: grafana
├── replica: 1
├── image: grafana/grafana:10.2.3
├── ports: 3000 (http)
├── env:
│   ├── GF_SECURITY_ADMIN_USER: admin
│   ├── GF_SECURITY_ADMIN_PASSWORD: (from secret)
│   └── GF_INSTALL_PLUGINS: piechart
├── volumeMounts:
│   ├── grafana-datasources
│   ├── grafana-dashboards-provider
│   └── grafana-storage (emptyDir)
└── resources:
    ├── requests: 100m CPU, 128Mi mem
    └── limits: 500m CPU, 512Mi mem

Service: grafana (NodePort 30300)

Secret: grafana-secret
└── admin-password: (base64 encoded)

ConfigMap: grafana-dashboards-provider
└── dashboards.yaml (provisioning config)
```

### Dashboard Files

#### **`k8s/monitoring/dashboards/mlflow-monitoring-dashboard.json`**
```json
{
  "title": "MLflow & Model Server Monitoring",
  "panels": [
    {
      "title": "MLflow Server Status",
      "query": "up{job=\"mlflow-server\"}"
    },
    {
      "title": "Model Server Status",
      "query": "up{job=\"model-server\"}"
    },
    {
      "title": "MLflow Request Latency (p95, p99)",
      "query": "histogram_quantile(...)"
    },
    {
      "title": "Model Server Request Rate",
      "query": "rate(http_requests_total...)"
    },
    {
      "title": "MLflow Error Rate",
      "query": "rate(http_requests_total...status=~...)"
    },
    {
      "title": "Model Server Error Rate",
      "query": "rate(http_requests_total...status=~...)"
    }
  ]
}
```

### Script Files

#### **`scripts/monitoring.sh`**
```bash
Functions:
├── check_prerequisites()
├── deploy_monitoring()
├── wait_for_deployment()
├── verify_deployment()
├── get_prometheus_url()
├── get_grafana_url()
├── setup_port_forwards()
├── check_targets()
├── check_status()
├── view_logs()
├── cleanup()
├── open_browser()
└── main() [dispatcher]

Commands:
├── deploy              # Deploy monitoring stack
├── status              # Show status
├── logs [component]    # View logs
├── prometheus-url      # Show Prometheus URLs
├── grafana-url         # Show Grafana URLs
├── port-forward        # Setup port-forwards
├── check-targets       # Check scrape targets
├── open-prometheus     # Open in browser
├── open-grafana        # Open in browser
├── cleanup             # Remove monitoring
└── help                # Show help
```

### Documentation Files

#### **`monitoring/README.md`**
```
Structure:
├── English version
│   ├── Overview
│   ├── Architecture
│   ├── Quick Start
│   ├── Monitoring Features
│   ├── Key Metrics
│   ├── Creating Custom Dashboards
│   ├── Viewing Alerts
│   ├── Data Retention & Storage
│   ├── Troubleshooting
│   ├── Performance Tuning
│   └── Integration with Kubernetes Events
│
└── Portuguese version
    └── [Same sections in PT-BR]
```

#### **`monitoring/IMPLEMENTATION_SUMMARY.md`**
```
├── Overview
├── Directory Structure
├── Quick Start
├── Components Deployed
├── Management Commands
├── Key Metrics to Monitor
├── Troubleshooting
├── Documentation Files
├── Next Steps
├── Configuration Reference
├── External Links
└── Implementation Checklist
```

#### **`monitoring/CHEATSHEET.md`**
```
├── Deploy
├── Access URLs
├── Prometheus Queries (PromQL)
├── Common Commands
├── Grafana Dashboards
├── Alert Rules
├── Troubleshooting Quick Fixes
├── Documentation Links
├── Common Workflows
├── Performance Tips
├── Security Notes
└── Quick Help
```

---

## 🎯 Use Case Scenarios & Navigation

### Scenario 1: Fresh Project Setup
1. Deploy: `./scripts/monitoring.sh deploy`
2. Access: `./scripts/monitoring.sh port-forward`
3. Verify: `./scripts/monitoring.sh check-targets`
4. View dashboard: http://127.0.0.1:3000

**Files used:** `prometheus-config.yaml`, `prometheus-grafana-deployment.yaml`, `monitoring.sh`

---

### Scenario 2: Learn Monitoring Concepts
1. Read: `README.md` → Overview → Architecture
2. Read: `monitoring/README.md` → Architecture → Key Metrics
3. Read notebook: Step 8 - Monitoring

**Files used:** `README.md`, `monitoring/README.md`, `.ipynb`

---

### Scenario 3: Create Custom Dashboard
1. Access Grafana: `./scripts/monitoring.sh port-forward`
2. Reference queries: `CHEATSHEET.md` → Prometheus Queries
3. Create dashboard in UI: + → Dashboard
4. Export JSON: share → export
5. Save to: `k8s/monitoring/dashboards/my-dashboard.json`

**Files used:** `CHEATSHEET.md`, Grafana UI, `dashboards/`

---

### Scenario 4: Debug Prometheus Not Scraping
1. Check status: `./scripts/monitoring.sh status`
2. Check targets: `./scripts/monitoring.sh check-targets`
3. View logs: `./scripts/monitoring.sh logs prometheus`
4. Troubleshoot: `monitoring/README.md` → Troubleshooting

**Files used:** `monitoring.sh`, `prometheus-config.yaml`, `README.md`

---

### Scenario 5: Configure Production Alerts
1. Edit: `k8s/monitoring/prometheus-config.yaml` (alert rules)
2. Apply: `kubectl apply -f k8s/monitoring/prometheus-config.yaml`
3. Test in Grafana: Alerting → Alert rules
4. Configure notifications: Grafana UI → Alerting

**Files used:** `prometheus-config.yaml`, Grafana UI

---

## 📞 Quick Navigation by Role

### **For Operators (Day-to-Day)**
1. `monitoring/CHEATSHEET.md` - Common commands
2. `scripts/monitoring.sh help` - Command reference
3. Grafana dashboards (browser)

### **For Developers (Customization)**
1. `monitoring/README.md` - Concepts
2. `k8s/monitoring/prometheus-config.yaml` - Scrape config
3. `k8s/monitoring/dashboards/` - Dashboard JSON
4. Grafana UI - Dashboard editor

### **For SREs (Production)**
1. `monitoring/IMPLEMENTATION_SUMMARY.md` - Overview
2. `monitoring/README.md` - Complete guide
3. `k8s/monitoring/prometheus-grafana-deployment.yaml` - K8s config
4. Alert rules in `prometheus-config.yaml`

### **For DevOps Engineers (Infrastructure)**
1. `k8s/monitoring/prometheus-grafana-deployment.yaml` - All manifests
2. `k8s/monitoring/prometheus-config.yaml` - Configuration
3. `monitoring/README.md` - Performance tuning section
4. `scripts/monitoring.sh` - Automation

---

## 🔗 Cross-Reference Map

```
Getting Started
    ↓
    ├─→ README.md (main) → Monitoring § Quick Start
    │   ├─→ scripts/monitoring.sh deploy
    │   └─→ monitoring/README.md
    │
    ├─→ notebooks/step-by-step_instructions_for_execution.ipynb (Step 8)
    │   ├─→ Deploy monitoring
    │   ├─→ Access Grafana/Prometheus
    │   └─→ Create custom dashboards
    │
    └─→ monitoring/CHEATSHEET.md
        ├─→ Common Commands
        ├─→ PromQL Queries
        └─→ Troubleshooting

Understanding Implementation
    ↓
    ├─→ monitoring/README.md
    │   ├─→ Architecture §
    │   ├─→ Components §
    │   └─→ Configuration Reference §
    │
    └─→ monitoring/IMPLEMENTATION_SUMMARY.md
        ├─→ Components Deployed §
        ├─→ Configuration Reference §
        └─→ Next Steps §

Customization
    ↓
    ├─→ k8s/monitoring/prometheus-config.yaml
    │   ├─→ scrape_configs (add targets)
    │   ├─→ rule_files (configure alerts)
    │   └─→ global (adjust intervals)
    │
    ├─→ k8s/monitoring/prometheus-grafana-deployment.yaml
    │   ├─→ Prometheus Deployment (resources)
    │   └─→ Grafana Deployment (env vars, plugins)
    │
    ├─→ k8s/monitoring/dashboards/
    │   └─→ Edit JSON directly
    │
    └─→ Grafana UI
        ├─→ Create dashboards visually
        ├─→ Configure alerts
        └─→ Add notification channels

Troubleshooting
    ↓
    ├─→ monitoring/CHEATSHEET.md → Troubleshooting Quick Fixes
    │
    ├─→ monitoring/README.md → Troubleshooting § (detailed)
    │
    ├─→ scripts/monitoring.sh
    │   ├─→ status (check health)
    │   ├─→ logs [component] (view errors)
    │   ├─→ check-targets (verify scraping)
    │   └─→ port-forward (local access)
    │
    └─→ kubectl commands (manual debugging)
```

---

## 📱 Index Summary

| Information | Located In | Command |
|-------------|-----------|---------|
| How to deploy | README.md § Monitoring | `./scripts/monitoring.sh deploy` |
| Available commands | monitoring/CHEATSHEET.md | `./scripts/monitoring.sh help` |
| Prometheus config | k8s/monitoring/prometheus-config.yaml | - |
| K8s manifests | k8s/monitoring/prometheus-grafana-deployment.yaml | `kubectl apply -f ...` |
| Dashboard JSON | k8s/monitoring/dashboards/ | - |
| Access URLs | monitoring/CHEATSHEET.md § Access URLs | `./scripts/monitoring.sh prometheus-url` |
| Port forwards | monitoring/CHEATSHEET.md § Access URLs | `./scripts/monitoring.sh port-forward` |
| PromQL examples | monitoring/CHEATSHEET.md § Prometheus Queries | - |
| Troubleshooting | monitoring/README.md § Troubleshooting | `./scripts/monitoring.sh logs` |
| Quick reference | monitoring/IMPLEMENTATION_SUMMARY.md | - |
| Full guide | monitoring/README.md | - |

---

## ✅ File Checklist

- ✅ `k8s/monitoring/prometheus-config.yaml` - Main Prometheus config
- ✅ `k8s/monitoring/prometheus-grafana-deployment.yaml` - K8s manifests
- ✅ `k8s/monitoring/dashboards/mlflow-monitoring-dashboard.json` - Pre-built dashboard
- ✅ `monitoring/README.md` - Complete guide (EN/PT-BR)
- ✅ `monitoring/IMPLEMENTATION_SUMMARY.md` - Implementation reference
- ✅ `monitoring/CHEATSHEET.md` - Quick command reference
- ✅ `monitoring/INDEX.md` - This navigation guide
- ✅ `scripts/monitoring.sh` - Automation script
- ✅ `README.md` - Main README (has monitoring §)
- ✅ `notebooks/step-by-step_instructions_for_execution.ipynb` - Step 8 (notebook)

---

**Last Updated:** February 19, 2026  
**Total Files:** 10 core monitoring files  
**Documentation:** ~4000+ lines total  
**Status:** ✅ Complete & Production Ready

---

**Start Here:** [monitoring/README.md](./README.md) or [monitoring/CHEATSHEET.md](./CHEATSHEET.md)
