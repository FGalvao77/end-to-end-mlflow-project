# Kubernetes Deployment Guide

Esta pasta contém manifests YAML para deployar a aplicação MLflow no Kubernetes (K8s).

## ⚠️ IMMEDIATELY: Start Minikube (if not running)

Antes de qualquer comando kubectl, você precisa de um cluster Kubernetes ativo. A forma mais simples é via **Minikube**.

### Verificar se Minikube está rodando

```bash
minikube status
```

Se retornar `host: Running, kubelet: Running, apiserver: Running`, pule para a secção **Pré-requisitos**.

### Iniciar Minikube (primeira vez ou após parar)

```bash
# Iniciar cluster (pode levar alguns minutos)
minikube start

# Verificar status
minikube status

# Confirmar conectividade com kubectl
kubectl cluster-info
kubectl get nodes
```

---

## Pré-requisitos

- **kubectl** instalado e configurado para o seu cluster K8s
- **Minikube** instalado e em execução
- **Docker image** `my-mlflow-app:latest` disponível no registry do cluster
- **PersistentVolume** suportado (para armazenar dados do MLflow)
- Acesso a pelo menos **2 nodes** (para 2 réplicas por serviço)

## Instalação de Ferramentas

### kubectl (Linux/macOS)

```bash
# Download and install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
kubectl version --client
```

### Minikube (Local Testing)

```bash
# Install Minikube
curl -LO https://github.com/kubernetes/minikube/releases/latest/download/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start Minikube cluster
minikube start --cpus=4 --memory=8192

# Confirm cluster is running
kubectl cluster-info
kubectl get nodes
```

## Deployment

### 1. Preparar Imagem Docker

Certifique-se de que a imagem está disponível no seu cluster:

```bash
# Se usar Minikube, carregue a imagem local:
minikube image build -t my-mlflow-app:latest -f src/mlops_project/Dockerfile .

# Ou construa dentro do Minikube Docker daemon:
eval $(minikube docker-env)
docker build -t my-mlflow-app:latest -f src/mlops_project/Dockerfile .
```

Para **clusters cloud** (EKS, GKE, AKS):
```bash
# Tag e push para seu registry (ex: Docker Hub ou ECR)
docker tag my-mlflow-app:latest your-registry/my-mlflow-app:latest
docker push your-registry/my-mlflow-app:latest

# Atualizar `imagePullPolicy` em mlflow-deployment.yaml para `Always`
# e mudar `image` para seu registry
```

### 2. Aplicar Manifests

```bash
# Criar namespace e resources do zero
kubectl apply -f k8s/mlflow-deployment.yaml

# Verificar status
kubectl get all -n mlflow-prod
kubectl get pvc -n mlflow-prod
```

### 3. Acessar Serviços

**Em Minikube:**
```bash
# Obtenha endpoint nodePort
minikube service mlflow-service -n mlflow-prod
minikube service model-service -n mlflow-prod

# Ou use port-forward
kubectl port-forward svc/mlflow-service -n mlflow-prod 5000:5000 &
kubectl port-forward svc/model-service -n mlflow-prod 8000:8000 &

# UIdo MLflow: http://localhost:5000
# Model Server: http://localhost:8000/ping
```

**Em Clusters Cloud (NodePort):**
```bash
# Obtenha o IP do Node
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')

# MLflow UI
http://$NODE_IP:30500

# Model Server
http://$NODE_IP:30800/ping
```

## Monitoramento

### Logs

```bash
# MLflow Server
kubectl logs -n mlflow-prod -l app=mlflow-server -f

# Model Server
kubectl logs -n mlflow-prod -l app=model-server -f

# Logs de um pod específico
kubectl logs -n mlflow-prod <pod-name> -c mlflow
```

### Status dos Pods

```bash
# Listar todos os pods
kubectl get pods -n mlflow-prod

# Detalhar um pod
kubectl describe pod -n mlflow-prod <pod-name>

# Ver eventos do cluster
kubectl get events -n mlflow-prod --sort-by='.lastTimestamp'
```

### Verificar Readiness/Liveness

```bash
# Verificar saúde dos endpoints
kubectl get endpoints -n mlflow-prod

# Health check manual
POD_IP=$(kubectl get pod -n mlflow-prod -l app=mlflow-server -o jsonpath='{.items[0].status.podIP}')
curl http://$POD_IP:5000/health

MODEL_IP=$(kubectl get pod -n mlflow-prod -l app=model-server -o jsonpath='{.items[0].status.podIP}')
curl http://$MODEL_IP:8000/ping
```

## Escalamento

### Manual

```bash
# Escalar MLflow Server para 3 replicas
kubectl scale deployment mlflow-server -n mlflow-prod --replicas=3

# Escalar Model Server para 5 replicas
kubectl scale deployment model-server -n mlflow-prod --replicas=5

# Verificar
kubectl get deploy -n mlflow-prod
```

### Automático (HPA)

O HPA já está configurado em `mlflow-deployment.yaml`:
- **Model Server**: min 2, max 5 replicas, 70% CPU / 80% memória

```bash
# Ver status do HPA
kubectl get hpa -n mlflow-prod -w

# Editar limites
kubectl edit hpa model-server-hpa -n mlflow-prod
```

## Storage Persistente

O manifesto cria um `PersistentVolumeClaim` de 10Gi para armazenar:
- Banco de dados SQLite do MLflow (`/mlruns/mlflow.db`)
- Artifacts do modelo (`/mlruns/artifacts`)

```bash
# Verificar status do PVC
kubectl get pvc -n mlflow-prod

# Se precisar remover (cuidado: deleta dados!)
kubectl delete pvc mlflow-pvc -n mlflow-prod
```

## Limpeza

```bash
# Remover todos os resources do namespace
kubectl delete namespace mlflow-prod

# Remover apenas deploys e services (mantém PVC)
kubectl delete -f k8s/mlflow-deployment.yaml
```

## Troubleshooting

### Pods em "Pending"

```bash
# Verificar recursos disponíveis no cluster
kubectl describe nodes

# Ver events do pod
kubectl describe pod <pod-name> -n mlflow-prod
```

### Imagem não encontrada

```bash
# Confirme que a imagem está no registry
docker images | grep my-mlflow-app

# Se usar Minikube, carregue a imagem
minikube image load my-mlflow-app:latest
```

### Serviço não está acessível

```bash
# Verificar se Service tem endpoints
kubectl get endpoints mlflow-service -n mlflow-prod

# Verificar logs do pod
kubectl logs <pod-name> -n mlflow-prod

# Verificar portas abertas
kubectl get svc mlflow-service -n mlflow-prod
```

## CI/CD Integration (GitHub Actions)

Exemplo de workflow para deploy automático:

```yaml
# .github/workflows/deploy-k8s.yml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build and push Docker image
        run: |
          docker build -t my-mlflow-app:${{ github.sha }} -f src/mlops_project/Dockerfile .
          docker push my-registry/my-mlflow-app:${{ github.sha }}
      
      - name: Deploy to K8s
        run: |
          kubectl apply -f k8s/mlflow-deployment.yaml
          kubectl set image deployment/model-server model=my-registry/my-mlflow-app:${{ github.sha }} -n mlflow-prod
```

## Deployando FastAPI para Model Serving

### FastAPI REST API

A aplicação inclui um **FastAPI REST API** para servir previsões via HTTP com Prometheus metrics integrado.

**Características:**
- ✅ 13 endpoints REST (health, predict, batch, metrics, docs)
- ✅ Auto-scaling (2-5 replicas com HPA)
- ✅ Health checks para K8s
- ✅ Prometheus metrics (/metrics)
- ✅ Swagger UI (/docs)

### Deploy FastAPI

```bash
# 1. Deploy FastAPI API
kubectl apply -f k8s/fastapi-deployment.yaml

# 2. Verificar status
kubectl get all -n mlflow-prod | grep fastapi

# 3. Port-forward para teste local
kubectl port-forward svc/fastapi-service -n mlflow-prod 8000:8000 &

# 4. Testar API
curl -s http://localhost:8000/health | jq .

# 5. Acessar documentação interativa
# Abra http://localhost:8000/docs no navegador
```

### Documentação FastAPI

Para documentação detalhada:
- [fastapi-api/README.md](../fastapi-api/README.md)
- [fastapi-api/ENDPOINTS.md](../fastapi-api/ENDPOINTS.md)
- [fastapi-api/CHEATSHEET.md](../fastapi-api/CHEATSHEET.md)

## Referências

- [Kubernetes Docs](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [MLflow Deployment Guide](https://mlflow.org/docs/latest/deployment/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
