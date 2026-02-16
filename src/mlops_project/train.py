from load_prepare_data import load_data, prepare_data
from utils import load_config

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (classification_report, 
                             confusion_matrix, 
                             ConfusionMatrixDisplay,
                             roc_curve,
                             RocCurveDisplay,
                             precision_score, 
                             recall_score, 
                             f1_score)

import matplotlib.pyplot as plt
plt.style.use(style='ggplot')

from pathlib import Path

from joblib import dump

import os
import shutil

import warnings
warnings.filterwarnings(action='ignore', category=FutureWarning)

USE_MLFLOW = False
try:
    import mlflow, mlflow.sklearn 
    USE_MLFLOW = True
except Exception:
    USE_MLFLOW = False

def main():
    config = load_config(file_path='configs.yaml')
    print(f'CONFIG: {config}')

    X, y = load_data(as_frame=False)
    X_train, X_test, y_train, y_test = prepare_data(X=X, y=y, size=config['test_size'], 
                                                    random_state=config['random_state'], 
                                                    stratify=config['stratify'])
    print(f'SHAPES: {X_train.shape}, {X_test.shape}, {y_train.shape}, {y_test.shape}')

    pipe = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('rf_model', RandomForestClassifier(**config['model']['params']))
    ])

    pipe.fit(X=X_train, y=y_train)
    y_pred = pipe.predict(X=X_test)
    y_pred_proba = pipe.predict_proba(X=X_test)[:, 1]

    metrics = {
        'accuracy': pipe.score(X=X_test, y=y_test),
        'precision': precision_score(y_true=y_test, y_pred=y_pred),
        'recall': recall_score(y_true=y_test, y_pred=y_pred),
        'f1_score': f1_score(y_true=y_test, y_pred=y_pred)
    }
    print(f'METRICS: {metrics}')

    classification_rep = classification_report(y_true=y_test, y_pred=y_pred)
    print(f'CLASSIFICATION REPORT:\n{classification_rep}')
    
    # Salvar métricas em arquivo txt
    metrics_dir = Path(config['paths']['metrics']).resolve()
    metrics_dir.mkdir(parents=True, exist_ok=True)
    
    with open(metrics_dir / 'metrics.txt', 'w') as f:
        f.write('MODEL METRICS\n')
        f.write('=' * 50 + '\n\n')
        for key, value in metrics.items():
            f.write(f'{key}: {value}\n')
        f.write('\n' + '=' * 50 + '\n')
        f.write('CLASSIFICATION REPORT\n')
        f.write('=' * 50 + '\n')
        f.write(classification_rep)
    
    print(f'Metrics saved to: {metrics_dir / "metrics.txt"}')
    
    cm = confusion_matrix(y_true=y_test, y_pred=y_pred)

    plt.figure(figsize=(8, 8))
    ConfusionMatrixDisplay(confusion_matrix=cm,
                           display_labels=pipe.classes_).plot(cmap='Blues')

    plt.title('Confusion Matrix - Random Forest Model\n', 
              fontdict={
                  'fontsize': 15,
                  'fontweight': 'bold'
          })
    
    plt.xlabel(xlabel='Predicted Label', fontsize=12)
    plt.ylabel(ylabel='True Label', fontsize=12)
    plt.grid(visible=False)
    plt.tight_layout()


    exported = Path(config['paths']['exported_model_dir']).resolve()
    plots_dir = Path(config['paths']['plots']).resolve()

    # Limpar o diretório se já existir
    if exported.exists():
        shutil.rmtree(exported)
    
    exported.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    # Salvar matriz de confusão em artifacts/plots
    plt.savefig(plots_dir / 'confusion_matrix.png', dpi=300, bbox_inches='tight')
    print(f'Confusion matrix saved to: {plots_dir / "confusion_matrix.png"}')
    plt.close()
    
    # Gerar e salvar curva ROC
    plt.figure(figsize=(8, 6))
    RocCurveDisplay.from_predictions(y_test, y_pred_proba, 
                                     name='Random Forest').plot()
    plt.title('ROC Curve - Random Forest Model\n', 
              fontdict={'fontsize': 15, 
                        'fontweight': 'bold'})
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.grid(visible=True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(plots_dir / 'roc_curve.png', dpi=300, bbox_inches='tight')
    print(f'ROC curve saved to: {plots_dir / "roc_curve.png"}')
    plt.close()

    dump(value=pipe, filename=exported / 'model.joblib')
    print(f'Model saved to: {exported / "model.joblib"}')

    if USE_MLFLOW:
        # Limpar o diretório antes do MLflow salvar (MLflow exige diretório vazio)
        if exported.exists():
            shutil.rmtree(exported)
        exported.mkdir(parents=True, exist_ok=True)
        
        mlflow.sklearn.save_model(sk_model=pipe, path=exported)
        print(f'Model saved to: {exported}')

        if (os.getenv(key='MLFLOW_TRACKING_URI') is not None) and (os.getenv(key='MLFLOW_EXPERIMENT_NAME') is not None):
            mlflow.set_tracking_uri(uri=os.getenv(key='MLFLOW_TRACKING_URI'))
            mlflow.set_experiment(experiment_name=os.getenv(key='MLFLOW_EXPERIMENT_NAME'))
            print(f'MLflow tracking URI: {os.getenv(key="MLFLOW_TRACKING_URI")}')
            print(f'MLflow experiment name: {os.getenv("MLFLOW_EXPERIMENT_NAME")}')

            with mlflow.start_run(run_name=os.getenv('MLFLOW_RUN_NAME', 'train')):
                for key, value in config.items():
                    mlflow.log_param(key=key, value=value)
                for key, value in metrics.items():
                    mlflow.log_metric(key=key, value=value)
                mlflow.sklearn.log_model(sk_model=pipe, artifact_path='model')
                mlflow.sklearn.save_model(sk_model=pipe, path=exported / 'model.pkl')
                print(f'Model saved to: {exported / "model.pkl"}')
        else:
            print('MLflow tracking URI or experiment name not set. Skipping MLflow logging.') 
    else:
        print('MLflow is not installed. Skipping MLflow logging.')

if __name__ == '__main__':
    main()