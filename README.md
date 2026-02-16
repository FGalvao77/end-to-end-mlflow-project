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
    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_metric("accuracy", 0.92)
    mlflow.sklearn.log_model(model, "model")
```

---

## ▶️ Como Executar / How to Run

### Instalação / Installation
```bash
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

### MLflow UI
```bash
mlflow ui
```
Acesse / Access: `http://127.0.0.1:5000`

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
