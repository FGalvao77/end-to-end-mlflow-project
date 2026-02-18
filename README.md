# 🚀 End-to-End MLflow Project

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![MLflow](https://img.shields.io/badge/MLOps-MLflow-orange?logo=mlflow)
![GitHub Actions](https://img.shields.io/badge/CI/CD-GitHub%20Actions-lightgrey?logo=githubactions&logoColor=blue)
![Lint](https://img.shields.io/badge/Lint-Flake8-yellow?logo=python)
![Tests](https://img.shields.io/badge/Tests-Pytest-green?logo=pytest)
![License](https://img.shields.io/badge/License-MIT-success?logo=open-source-initiative)

---

## 📖 Visão Geral (PT-BR)
Este projeto demonstra a construção de um pipeline **end-to-end de Machine Learning** com **MLflow**, cobrindo todas as etapas de **MLOps**:  
- Ingestão e pré-processamento de dados  
- Treinamento e rastreamento de experimentos  
- Avaliação e seleção de modelos  
- Deployment em ambiente produtivo  

O objetivo é servir como um **cartão de visitas técnico**, mostrando experiência prática em **engenharia de machine learning aplicada a produção**.

---

## 📖 Overview (EN)
This project demonstrates the implementation of an **end-to-end Machine Learning pipeline** using **MLflow**, covering all **MLOps** stages:  
- Data ingestion and preprocessing  
- Model training and experiment tracking  
- Model evaluation and selection  
- Deployment into production environment  

The goal is to serve as a **technical portfolio project**, showcasing practical experience in **machine learning engineering applied to production**.

---

## 🏗️ Arquitetura / Architecture
```
end-to-end-mlflow-project/
│── src/
│   └── mlops_project/
│       ├── data_preprocessing.py   # Limpeza / Data preprocessing
│       ├── train.py                # Treinamento / Training
│       ├── evaluate.py             # Avaliação / Evaluation
│       └── deploy.py               # Deployment
│── requirements.txt                # Dependências / Dependencies
│── README.md                       # Documentação / Documentation
│── .gitignore                      # Versionamento / Versioning
```

---

## ⚙️ Tecnologias / Technologies
- **Python 3.9+**  
- **MLflow** (Tracking, Models, UI)  
- **Git + GitHub** for version control  
- Modular structure following engineering best practices  

---

## 🔬 MLflow – Integração / Integration
O projeto utiliza **MLflow Tracking** e **MLflow Models** para:  
The project uses **MLflow Tracking** and **MLflow Models** for:  
- Registro automático de parâmetros, métricas e artefatos / Automatic logging of parameters, metrics, and artifacts  
- Padronização de modelos para deployment / Standardized model packaging for deployment  
- Comparação de experimentos via MLflow UI / Experiment comparison via MLflow UI  

Exemplo / Example:
```python
import mlflow

with mlflow.start_run():
    mlflow.log_param('model_type', 'RandomForest')
    mlflow.log_metric('accuracy', 0.92)
    mlflow.sklearn.log_model(model, 'model')
```

---

## ▶️ Como Executar / How to Run

### Instalação / Installation
```bash
# create a Python virtual environment and activate it
python -m venv .venv
source .venv/bin/activate

# clone repository and install dependencies
git clone https://github.com/FGalvao77/end-to-end-mlflow-project.git
cd end-to-end-mlflow-project
pip install -r requirements.txt
```

### Pipeline
```bash
python src/mlops_project/data_preprocessing.py
python src/mlops_project/train.py
python src/mlops_project/evaluate.py
python src/mlops_project/deploy.py
```

### Running the test suite
The repository includes simple unit tests for training, evaluation and
deployment logic.  To execute them (from the project root) run:

```bash
.venv/bin/python -m pytest -q
```

The helper `train.train_model()` used by the tests sets up an isolated
file‑based tracking store so the tests never require an MLflow server and
don't leave garbage behind.

### MLflow UI
By default the training script uses a **file-based tracking store** located
inside the project (`mlruns/`).  This means you can run the pipeline without
having an MLflow server running and you won't see any connection errors
(see `src/mlops_project/train.py` for details).

If you prefer to run an MLflow server inside Docker you can use the
provided compose file.  Start it after you have activated your virtual
environment:

```bash
export DOCKER_API_VERSION=1.44
docker compose -f docker-compose.mlflow.yml up -d
```

The UI will be available at `http://127.0.0.1:5000` unless you override the
port.  You can also point the code at a remote tracking server by setting
`MLFLOW_TRACKING_URI` in your environment, e.g.: 

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
```

If you prefer to use the standalone server or view experiments through the
web UI, start it in the project root before running `train.py`:

```bash
mlflow ui
```

The UI will be available at `http://127.0.0.1:5000` unless you override the
port.  You can also point the code at a remote tracking server by setting
`MLFLOW_TRACKING_URI` in your environment, e.g.: 

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
```

### Handling corrupted tracking stores
The training script now automatically cleans up any non‑numeric subdirectories
under `mlruns/` at startup – these are usually created when the
`MLFLOW_ARTIFACT_URI` was mis‑configured and they can lead to warnings or
failures such as the ``MissingConfigException`` shown above.  If you ever
experience errors during MLflow logging you can safely remove the entire
``mlruns/`` directory:

```bash
rm -rf mlruns
```

Additionally the script prints warnings and continues if it is unable to log a
model (e.g. due to a missing ``meta.yaml`` or permission error), so training
itself will not abort just because of MLflow issues.

> **Tip:** you can inspect the output for messages prefixed with ``WARNING:``
> to understand why MLflow logging may have failed; these will not stop the
> pipeline from producing artifacts in the `artifacts/` folder.

---

## ✅ Boas Práticas / Best Practices
- Estrutura modular e escalável / Modular and scalable structure  
- Versionamento limpo com `.gitignore` / Clean versioning with `.gitignore`  
- Registro completo de experimentos com MLflow / Complete experiment tracking with MLflow  
- Separação clara entre **ETL, treinamento, avaliação e deployment** / Clear separation of **ETL, training, evaluation, and deployment**  
- Documentação técnica voltada para recrutadores / Technical documentation tailored for recruiters  

---

## 🔮 Extensões Futuras / Future Extensions
- Integração com **Docker/Kubernetes** / Integration with **Docker/Kubernetes**  
- Automação de pipeline com **CI/CD (GitHub Actions)** / Pipeline automation with **CI/CD (GitHub Actions)**  
- Monitoramento de modelos em produção / Model monitoring in production  
- Inclusão de testes unitários e integração contínua / Unit testing and continuous integration  

---

## 📌 Conclusão / Conclusion
Este projeto exemplifica um pipeline moderno de **MLOps**, destacando:  
This project exemplifies a modern **MLOps pipeline**, highlighting:  
- **Rigor técnico / Technical rigor**  
- **Boas práticas de engenharia / Engineering best practices**  
- **Capacidade de deployment real / Real deployment capability**  

👉 Ele serve como uma vitrine para recrutadores, demonstrando experiência prática em **Machine Learning aplicado a produção**.  
👉 It serves as a showcase for recruiters, demonstrating practical experience in **Machine Learning applied to production**.

---
