# Monitoring & Observability with Prometheus and Grafana
# Monitoramento e Observabilidade com Prometheus e Grafana

## English

### Overview

This monitoring stack provides comprehensive observability for your MLflow deployment using Prometheus and Grafana. It enables real-time metrics collection, visualization, and alerting for both the MLflow server and model serving infrastructure.

**Key Features:**
- Real-time metrics collection from MLflow server and model servers
- Pre-built Grafana dashboards for monitoring
- Alert rules for critical system and model events
- Kubernetes-native deployment with high availability
- 30-day metrics retention

### Architecture

```
┌─────────────────────────────────────────────┐
│        MLflow Server & Model Server         │
│         (Expose /metrics endpoints)         │
└────────────────┬────────────────────────────┘
                 │ scrape (port 9090)
                 ▼
         ┌───────────────┐
         │  Prometheus   │
         │  (Port 9090)  │
         │  Storage: 30d │
         └───────┬───────┘
                 │ query
                 ▼
         ┌───────────────┐
         │    Grafana    │
         │  (Port 3000)  │
         │  Dashboards   │
         │   & Alerts    │
         └───────────────┘
```

### Quick Start

#### ⚠️ Prerequisite: Minikube must be running

Before deploying the monitoring stack, ensure your Kubernetes cluster is active:

```bash
minikube status
# Must show: host: Running, kubelet: Running, apiserver: Running
```

If not running, start it:
```bash
minikube start
```

Verify connectivity:
```bash
kubectl cluster-info
kubectl get nodes
```

#### 1. Deploy Monitoring Stack

```bash
# Create all monitoring components
kubectl apply -f k8s/monitoring/prometheus-config.yaml
kubectl apply -f k8s/monitoring/prometheus-grafana-deployment.yaml

# Verify deployment
kubectl get all -n mlflow-prod
```

#### 2. Access Prometheus

**Kubernetes Port-Forward (recommended for development):**
```bash
kubectl port-forward svc/prometheus -n mlflow-prod 9090:9090
```

**Via NodePort (Kubernetes):**
- URL: http://<NODE_IP>:30090
- From Minikube: `minikube service prometheus -n mlflow-prod`

**Check Prometheus Targets:**
```bash
curl -s http://127.0.0.1:9090/api/v1/targets | jq .
```

#### 3. Access Grafana

**Port-Forward:**
```bash
kubectl port-forward svc/grafana -n mlflow-prod 3000:3000
```

**Via NodePort:**
- URL: http://<NODE_IP>:30300
- From Minikube: `minikube service grafana -n mlflow-prod`

**Default Credentials:**
- Username: `admin`
- Password: `admin123456789`

### Monitoring Features

#### Prometheus Scrape Targets

| Target | Job Name | Path | Interval |
|--------|----------|------|----------|
| MLflow Server | `mlflow-server` | `/metrics` | 10s |
| Model Server | `model-server` | `/metrics` | 10s |
| Prometheus | `prometheus` | `-` | 15s |
| Kubernetes API | `kubernetes-apiservers` | - | - |
| Kubernetes Nodes | `kubernetes-nodes` | - | - |
| Kubernetes Pods | `kubernetes-pods` | - | - |

#### Pre-configured Alert Rules

**Critical Alerts:**
- `MLflowServerDown` - MLflow server unreachable (1m threshold)
- `ModelServerDown` - Model server unreachable (1m threshold)
- `PodCrashLooping` - Pod restarting frequently (5m threshold)

**Warning Alerts:**
- `HighCPUUsage` - CPU > 80% for 5 minutes
- `HighMemoryUsage` - Memory > 85% for 5 minutes
- `HighModelLatency` - p95 latency > 1 second
- `MLflowExperimentFailure` - Training run failed

### Key Metrics

#### MLflow Server Metrics
```
mlflow_runs_created_total        # Total runs created
mlflow_runs_finished_total       # Total runs finished
mlflow_runs_finished_total{status="FAILED"}  # Failed runs
mlflow_experiment_* 

# HTTP Request Metrics
http_request_duration_seconds_bucket  # Request latency distribution
http_requests_total                   # Total requests by method/path
http_requests_total{status=~"4..|5.."}  # Errors (4xx, 5xx)
```

#### Model Server Metrics
```
mlflow_model_request_duration_seconds  # Inference latency
mlflow_predictions_total               # Total predictions
mlflow_model_* 

# HTTP Metrics (same as MLflow)
http_request_duration_seconds_bucket
http_requests_total
```

#### System Metrics (from Kubernetes)
```
node_cpu_seconds_total           # Node CPU usage
node_memory_MemAvailable_bytes   # Available memory
container_cpu_usage_seconds_total # Container CPU
container_memory_usage_bytes      # Container memory
```

### Creating Custom Dashboards

#### Via Grafana UI

1. Login to Grafana (http://localhost:3000)
2. Click **+** → **Dashboard** → **New Dashboard**
3. Click **Add a new panel**
4. Select **Prometheus** as datasource
5. Enter PromQL query (examples below)
6. Configure visualization and save

#### Example Queries

**MLflow Request Success Rate (last 1h):**
```promql
sum(rate(http_requests_total{job="mlflow-server", status="200"}[5m])) /
sum(rate(http_requests_total{job="mlflow-server"}[5m])) * 100
```

**Model Inference Throughput:**
```promql
sum(rate(http_requests_total{job="model-server", path="/invocations"}[5m])) by (status)
```

**Memory Usage by Pod:**
```promql
sum(container_memory_usage_bytes{namespace="mlflow-prod"}) by (pod)
```

**Experiment Success Rate:**
```promql
sum(increase(mlflow_runs_finished_total{status="FINISHED"}[1h])) /
(sum(increase(mlflow_runs_finished_total[1h]))) * 100
```

### Viewing Alerts

**In Prometheus:**
```bash
curl -s http://127.0.0.1:9090/api/v1/alerts | jq .
```

**In Grafana:**
1. Click **Alerting** → **Alert rules** (bell icon)
2. View active and pending alerts
3. Configure notification channels if needed

### Data Retention & Storage

- **Retention Period:** 30 days (via `--storage.tsdb.retention.time=30d`)
- **Storage:** tmpfs (emptyDir in Kubernetes) - persists for pod lifetime
- **For persistent metrics:** Modify deployment to use PersistentVolumeClaim

**Increase Retention:**
```bash
kubectl set env deployment/prometheus -n mlflow-prod \
  PROMETHEUS_RETENTION_TIME=365d
```

### Troubleshooting

#### Prometheus Targets Not Scraping

```bash
# Check Prometheus logs
kubectl logs -f deployment/prometheus -n mlflow-prod

# Verify service discovery
curl -s http://127.0.0.1:9090/service-discovery

# Test connectivity to target
kubectl exec -it deployment/prometheus -n mlflow-prod -- \
  curl -v http://mlflow-service.mlflow-prod.svc.cluster.local:5000/metrics
```

#### Grafana Not Connecting to Prometheus

1. Check datasource configuration:
   - Grafana UI → **Configuration** → **Data Sources**
   - Verify URL: `http://prometheus:9090`
   - Click **Test** button

2. Check pod-to-pod connectivity:
```bash
kubectl exec -it deployment/grafana -n mlflow-prod -- \
  curl -v http://prometheus:9090/-/healthy
```

#### High Memory Usage

Prometheus stores metrics in memory before writing to disk. For large deployments:
```yaml
# Modify prometheus deployment args:
- '--query.max-memory-samples=10000000'  # Default: 10M
- '--query.timeout=5m'
```

### Performance Tuning

#### Reduce Cardinality (high memory/CPU)
```yaml
# In prometheus-config.yaml, add metric relabeling:
metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'node_(network|netdev|softnet).*'
    action: drop  # Drop high-cardinality metrics
```

#### Adjust Scrape Intervals
```yaml
# Increase interval for less frequent monitoring
scrape_interval: 30s  # Default: 15s
```

#### Increase Prometheus Resources
```yaml
resources:
  requests:
    cpu: 500m      # Default: 100m
    memory: 2Gi    # Default: 256Mi
  limits:
    cpu: 2000m
    memory: 4Gi
```

### Integration with Kubernetes Events

The Prometheus configuration already includes Kubernetes service discovery:
- **API Server:** Metrics directly from Kubernetes API
- **Nodes:** Kubelet metrics from each node
- **Pods:** Auto-discovered pods with `prometheus.io/scrape: "true"` annotation

To monitor your MLflow/model pods, add annotations:
```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "5000"      # or 8000 for model server
  prometheus.io/path: "/metrics"
```

---

## Português

### Visão Geral

Esse stack de monitoramento fornece observabilidade abrangente para sua implantação MLflow usando Prometheus e Grafana. Permite coleta de métricas em tempo real, visualização e alertas para o servidor MLflow e a infraestrutura de serving de modelos.

**Principais Recursos:**
- Coleta de métricas em tempo real do servidor MLflow e servidor de modelos
- Dashboards Grafana pré-configurados para monitoramento
- Regras de alerta para eventos críticos do sistema e modelo
- Implantação nativa do Kubernetes com alta disponibilidade
- Retenção de métricas por 30 dias

### Arquitetura

```
┌─────────────────────────────────────────────┐
│   Servidor MLflow & Servidor de Modelo      │
│     (Expõem endpoints /metrics)             │
└────────────────┬────────────────────────────┘
                 │ scrape (porta 9090)
                 ▼
         ┌───────────────┐
         │  Prometheus   │
         │  (Porta 9090) │
         │ Armazenamento │
         │      30d      │
         └───────┬───────┘
                 │ consulta
                 ▼
         ┌───────────────┐
         │    Grafana    │
         │ (Porta 3000)  │
         │  Dashboards   │
         │    & Alertas  │
         └───────────────┘
```

### Início Rápido

#### 1. Implante o Stack de Monitoramento

```bash
# Crie todos os componentes de monitoramento
kubectl apply -f k8s/monitoring/prometheus-config.yaml
kubectl apply -f k8s/monitoring/prometheus-grafana-deployment.yaml

# Verifique a implantação
kubectl get all -n mlflow-prod
```

#### 2. Acesse Prometheus

**Port-Forward do Kubernetes (recomendado para desenvolvimento):**
```bash
kubectl port-forward svc/prometheus -n mlflow-prod 9090:9090
```

**Via NodePort (Kubernetes):**
- URL: http://<NODE_IP>:30090
- Do Minikube: `minikube service prometheus -n mlflow-prod`

**Verifique Targets do Prometheus:**
```bash
curl -s http://127.0.0.1:9090/api/v1/targets | jq .
```

#### 3. Acesse Grafana

**Port-Forward:**
```bash
kubectl port-forward svc/grafana -n mlflow-prod 3000:3000
```

**Via NodePort:**
- URL: http://<NODE_IP>:30300
- Do Minikube: `minikube service grafana -n mlflow-prod`

**Credenciais Padrão:**
- Usuário: `admin`
- Senha: `admin123456789`

### Recursos de Monitoramento

#### Targets do Prometheus para Scrape

| Alvo | Nome do Job | Caminho | Intervalo |
|------|-------------|---------|-----------|
| Servidor MLflow | `mlflow-server` | `/metrics` | 10s |
| Servidor de Modelo | `model-server` | `/metrics` | 10s |
| Prometheus | `prometheus` | `-` | 15s |
| API Kubernetes | `kubernetes-apiservers` | - | - |
| Nós Kubernetes | `kubernetes-nodes` | - | - |
| Pods Kubernetes | `kubernetes-pods` | - | - |

#### Regras de Alerta Pré-configuradas

**Alertas Críticos:**
- `MLflowServerDown` - Servidor MLflow indisponível (limite 1m)
- `ModelServerDown` - Servidor de modelo indisponível (limite 1m)
- `PodCrashLooping` - Pod reiniciando frequentemente (limite 5m)

**Alertas de Aviso:**
- `HighCPUUsage` - CPU > 80% por 5 minutos
- `HighMemoryUsage` - Memória > 85% por 5 minutos
- `HighModelLatency` - Latência p95 > 1 segundo
- `MLflowExperimentFailure` - Execução de treinamento falhou

### Métricas-Chave

#### Métricas do Servidor MLflow
```
mlflow_runs_created_total        # Total de execuções criadas
mlflow_runs_finished_total       # Total de execuções finalizadas
mlflow_runs_finished_total{status="FAILED"}  # Execuções falhadas
mlflow_experiment_* 

# Métricas de Requisitas HTTP
http_request_duration_seconds_bucket  # Distribuição de latência
http_requests_total                   # Total de requisições por método/caminho
http_requests_total{status=~"4..|5.."}  # Erros (4xx, 5xx)
```

#### Métricas do Servidor de Modelo
```
mlflow_model_request_duration_seconds  # Latência de inferência
mlflow_predictions_total               # Total de predições
mlflow_model_* 

# Métricas HTTP (mesmos que MLflow)
http_request_duration_seconds_bucket
http_requests_total
```

#### Métricas do Sistema (do Kubernetes)
```
node_cpu_seconds_total           # Uso de CPU do nó
node_memory_MemAvailable_bytes   # Memória disponível
container_cpu_usage_seconds_total # CPU do container
container_memory_usage_bytes      # Memória do container
```

### Criando Dashboards Personalizados

#### Via Interface Grafana

1. Faça login no Grafana (http://localhost:3000)
2. Clique em **+** → **Dashboard** → **Novo Dashboard**
3. Clique em **Adicionar novo painel**
4. Selecione **Prometheus** como fonte de dados
5. Insira consulta PromQL (exemplos abaixo)
6. Configure visualização e salve

#### Exemplos de Consultas

**Taxa de Sucesso de Requisições MLflow (última 1h):**
```promql
sum(rate(http_requests_total{job="mlflow-server", status="200"}[5m])) /
sum(rate(http_requests_total{job="mlflow-server"}[5m])) * 100
```

**Throughput de Inferência do Modelo:**
```promql
sum(rate(http_requests_total{job="model-server", path="/invocations"}[5m])) by (status)
```

**Uso de Memória por Pod:**
```promql
sum(container_memory_usage_bytes{namespace="mlflow-prod"}) by (pod)
```

**Taxa de Sucesso de Experimentos:**
```promql
sum(increase(mlflow_runs_finished_total{status="FINISHED"}[1h])) /
(sum(increase(mlflow_runs_finished_total[1h]))) * 100
```

### Visualizando Alertas

**No Prometheus:**
```bash
curl -s http://127.0.0.1:9090/api/v1/alerts | jq .
```

**No Grafana:**
1. Clique em **Alertas** → **Regras de Alerta** (ícone sino)
2. Veja alertas ativos e pendentes
3. Configure canais de notificação se necessário

### Retenção de Dados e Armazenamento

- **Período de Retenção:** 30 dias (via `--storage.tsdb.retention.time=30d`)
- **Armazenamento:** tmpfs (emptyDir no Kubernetes) - persiste pela vida útil do pod
- **Para métricas persistentes:** Modifique implantação para usar PersistentVolumeClaim

**Aumentar Período de Retenção:**
```bash
kubectl set env deployment/prometheus -n mlflow-prod \
  PROMETHEUS_RETENTION_TIME=365d
```

### Solução de Problemas

#### Targets Prometheus Não Scrapiando

```bash
# Verifique logs do Prometheus
kubectl logs -f deployment/prometheus -n mlflow-prod

# Verifique descoberta de serviço
curl -s http://127.0.0.1:9090/service-discovery

# Teste conectividade com o target
kubectl exec -it deployment/prometheus -n mlflow-prod -- \
  curl -v http://mlflow-service.mlflow-prod.svc.cluster.local:5000/metrics
```

#### Grafana Não se Conectando ao Prometheus

1. Verifique configuração da fonte de dados:
   - UI Grafana → **Configuração** → **Fontes de Dados**
   - Verifique URL: `http://prometheus:9090`
   - Clique no botão **Testar**

2. Verifique conectividade pod-a-pod:
```bash
kubectl exec -it deployment/grafana -n mlflow-prod -- \
  curl -v http://prometheus:9090/-/healthy
```

#### Alto Uso de Memória

Prometheus armazena métricas em memória antes de escrever em disco. Para implantações grandes:
```yaml
# Modifique argumentos da implantação do prometheus:
- '--query.max-memory-samples=10000000'  # Padrão: 10M
- '--query.timeout=5m'
```

### Otimização de Desempenho

#### Reduzir Cardinalidade (alto consumo de memória/CPU)
```yaml
# No prometheus-config.yaml, adicione relabeling de métrica:
metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'node_(network|netdev|softnet).*'
    action: drop  # Descarte métricas com alta cardinalidade
```

#### Ajustar Intervalos de Scrape
```yaml
# Aumente intervalo para monitoramento menos frequente
scrape_interval: 30s  # Padrão: 15s
```

#### Aumentar Recursos do Prometheus
```yaml
resources:
  requests:
    cpu: 500m      # Padrão: 100m
    memory: 2Gi    # Padrão: 256Mi
  limits:
    cpu: 2000m
    memory: 4Gi
```

### Integração com Eventos do Kubernetes

A configuração do Prometheus já inclui descoberta de serviço Kubernetes:
- **API Server:** Métricas diretamente da API Kubernetes
- **Nós:** Métricas do Kubelet de cada nó
- **Pods:** Pods descobertos automaticamente com anotação `prometheus.io/scrape: "true"`

Para monitorar seus pods MLflow/modelo, adicione anotações:
```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "5000"      # ou 8000 para servidor de modelo
  prometheus.io/path: "/metrics"
```

---

## Files Structure

```
k8s/monitoring/
├── prometheus-config.yaml              # Prometheus ConfigMap + PrometheusRules
├── prometheus-grafana-deployment.yaml  # Prometheus, Grafana, ServiceAccount, RBAC
├── dashboards/
│   └── mlflow-monitoring-dashboard.json  # Pre-built Grafana dashboard
└── README.md (this file)

monitoring/
└── README.md (this file - comprehensive guide)
```

## Next Steps

1. **Deploy Stack:**
   ```bash
   kubectl apply -f k8s/monitoring/prometheus-config.yaml
   kubectl apply -f k8s/monitoring/prometheus-grafana-deployment.yaml
   ```

2. **Access Services:**
   - Prometheus: `http://localhost:9090` (after port-forward)
   - Grafana: `http://localhost:3000` (default user: admin)

3. **Verify Targets:**
   - Go to Prometheus Targets page
   - Confirm MLflow and Model servers are "UP"

4. **Import Dashboard:**
   - Via Grafana UI: **+** → **Import** → Upload `mlflow-monitoring-dashboard.json`
   - Or configure ConfigMap-based provisioning (included in deployment)

5. **Set Up Alerts:**
   - Configure notification channels in Grafana
   - Update alert rules in `prometheus-config.yaml` as needed

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Kubernetes Monitoring](https://kubernetes.io/docs/tasks/run-application/monitor-application/)
- [MLflow Metrics API](https://mlflow.org/docs/latest/python_api/mlflow.html)
