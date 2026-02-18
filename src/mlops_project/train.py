# Author: Fernando Galvão
# Date: 2024-06-20
# Description: Script de treinamento do modelo de classificação utilizando Random Forest. O script inclui etapas de pré-processamento, treinamento, avaliação e salvamento do modelo, métricas e visualizações. O código é modularizado para facilitar a manutenção e a integração com pipelines de MLOps.

# Importações necessárias para o script
# attempt package-relative import; fall back to plain import if the module is
# executed as a standalone script (which places the parent directory on sys.path)
try:
    from .load_prepare_data import load_data, prepare_data
    from .utils import load_config
except ImportError:  # pragma: no cover - running as script
    from load_prepare_data import load_data, prepare_data
    from utils import load_config

# Bibliotecas para modelagem, avaliação e visualização
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
import uuid

# Ignorar warnings de FutureWarning para evitar poluição do output
import warnings
warnings.filterwarnings(action='ignore', category=FutureWarning)

# Verificar se MLflow está disponível para uso
USE_MLFLOW = False
try:
    import mlflow, mlflow.sklearn 
    USE_MLFLOW = True
except Exception:
    USE_MLFLOW = False

# Função principal do script de treinamento
def main():
    config = load_config(file_path='configs.yaml')
    print(f'CONFIG: {config}')

    # Carrega os dados usando a função load_data definida em load_prepare_data.py
    X, y = load_data(as_frame=False)
    # Dividir os dados em conjuntos de treino e teste usando a função prepare_data
    X_train, X_test, y_train, y_test = prepare_data(X=X, y=y, size=config['test_size'], 
                                                    random_state=config['random_state'], 
                                                    stratify=config['stratify'])
    # Exibir as formas dos conjuntos de treino e teste para verificação
    print(f'SHAPES: {X_train.shape}, {X_test.shape}, {y_train.shape}, {y_test.shape}')

    # Criar pipeline de pré-processamento e modelagem
    pipe = Pipeline(steps=[
        ('scaler', StandardScaler()),
        ('rf_model', RandomForestClassifier(**config['model']['params']))
    ])

    # Treinar o modelo e fazer previsões
    pipe.fit(X=X_train, y=y_train)
    y_pred = pipe.predict(X=X_test)

    # Obter probabilidades para a classe positiva (assumindo classificação binária)
    y_pred_proba = pipe.predict_proba(X=X_test)[:, 1]

    # Salvar os parâmetros do modelo em um arquivo txt
    params_dir = Path(config['paths']['params']).resolve()
    # Criar o diretório para salvar os parâmetros do modelo, se não existir
    params_dir.mkdir(parents=True, exist_ok=True)
    # Salvar os parâmetros do modelo em um arquivo txt
    with open(params_dir / 'model_params.txt', 'w') as f:
        f.write('MODEL PARAMETERS\n')
        f.write('=' * 50 + '\n\n')
        for key, value in config['model']['params'].items():
            f.write(f'{key}: {value}\n')
    print(f'Model parameters saved to: {params_dir / "model_params.txt"}')

    # Calcular métricas de avaliação
    metrics = {
        'accuracy': pipe.score(X=X_test, y=y_test),
        'precision': precision_score(y_true=y_test, y_pred=y_pred),
        'recall': recall_score(y_true=y_test, y_pred=y_pred),
        'f1_score': f1_score(y_true=y_test, y_pred=y_pred)
    }
    # Exibir métricas no console
    print(f'METRICS: {metrics}')

    # Gerar relatório de classificação detalhado
    classification_rep = classification_report(y_true=y_test, y_pred=y_pred)
    # Exibir relatório de classificação no console
    print(f'CLASSIFICATION REPORT:\n{classification_rep}')
    
    # Salvar métricas em arquivo txt
    metrics_dir = Path(config['paths']['metrics']).resolve()
    # Criar o diretório para salvar as métricas, se não existir
    metrics_dir.mkdir(parents=True, exist_ok=True)
    # Salvar as métricas e o relatório de classificação em um arquivo txt
    with open(metrics_dir / 'metrics.txt', 'w') as f:
        f.write('MODEL METRICS\n')
        f.write('=' * 50 + '\n\n')
        for key, value in metrics.items():
            f.write(f'{key}: {value}\n')
        f.write('\n' + '=' * 50 + '\n')
        f.write('CLASSIFICATION REPORT\n')
        f.write('=' * 50 + '\n')
        f.write(classification_rep)
    # Exibir caminho do arquivo de métricas salvo
    print(f'Metrics saved to: {metrics_dir / "metrics.txt"}')
    
    # Gerar e salvar matriz de confusão
    cm = confusion_matrix(y_true=y_test, y_pred=y_pred)
    # Exibir matriz de confusão no console
    print(f'Confusion Matrix:\n{cm}')

    # Configurar visualização da matriz de confusão
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

    # Configurar diretórios para salvar o modelo e as visualizações
    exported = Path(config['paths']['exported_model_dir']).resolve()

    # Configurar diretório para salvar as visualizações (plots)
    plots_dir = Path(config['paths']['plots']).resolve()

    # Limpar o diretório se já existir
    if exported.exists():
        shutil.rmtree(exported)
    
    # Criar os diretórios necessários para salvar o modelo e as visualizações
    exported.mkdir(parents=True, exist_ok=True)
    # Criar diretório para salvar as visualizações (plots)
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    # Salvar matriz de confusão em artifacts/plots
    plt.savefig(plots_dir / 'confusion_matrix.png', dpi=300, bbox_inches='tight')
    print(f'Confusion matrix saved to: {plots_dir / "confusion_matrix.png"}')
    plt.close()

    # Gerar dados para a curva ROC
    roc_curve_data = roc_curve(y_true=y_test, y_score=y_pred_proba)
    # Exibir dados da curva ROC no console (fpr, tpr, thresholds)
    print(f'ROC curve data (fpr, tpr, thresholds): \n{roc_curve_data}')
    roc_auc = pipe.score(X=X_test, y=y_test)
    print(f'ROC AUC: {roc_auc}')
    
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

    # Salvando os resultados de avaliação em um arquivo txt
    results_dir = Path(config['paths']['results']).resolve()
    # Criar o diretório para salvar os resultados de avaliação, se não existir
    results_dir.mkdir(parents=True, exist_ok=True)
    # Salvar as métricas, o relatório de classificação, a matriz de confusão e os dados da curva ROC em um arquivo txt
    with open(results_dir / 'evaluation_results.txt', 'w') as f:
        f.write('MODEL EVALUATION RESULTS\n')
        f.write('=' * 50 + '\n\n')
        f.write(f'Accuracy: {metrics["accuracy"]}\n')
        f.write(f'Precision: {metrics["precision"]}\n')
        f.write(f'Recall: {metrics["recall"]}\n')
        f.write(f'F1 Score: {metrics["f1_score"]}\n')
        f.write(f'ROC AUC: {roc_auc}\n')
        f.write('\n' + '=' * 50 + '\n')
        f.write('CLASSIFICATION REPORT\n')
        f.write('=' * 50 + '\n')
        f.write(classification_rep)
        f.write('\n' + '=' * 50 + '\n')
        f.write('Confusion Matrix\n')
        f.write('=' * 50 + '\n')
        f.write(str(cm))
        f.write('\n' + '=' * 50 + '\n')
        f.write('ROC Curve Data (fpr, tpr, thresholds)\n')
        f.write('=' * 50 + '\n')
        f.write(str(roc_curve_data))
        f.write('\n' + '=' * 50 + '\n')
    print(f'Evaluation results saved to: {results_dir / "evaluation_results.txt"}')

    # Salvar o modelo treinado usando joblib
    dump(value=pipe, filename=exported / 'model.joblib')
    # Exibir caminho do arquivo do modelo salvo
    print(f'Model saved to: {exported / "model.joblib"}')

    # Salvar o modelo usando MLflow, se disponível
    if USE_MLFLOW:
        # ensure the 'mlruns' directory exists and is writable by us; the
        # container may have created it as root which causes PermissionErrors
        # later when mlflow tries to create subfolders.  We also print a
        # helpful message so the user can fix things manually if needed.
        # ensure mlruns folder is always created at the project root (one
        # level above the package directory) so that repeated invocations
        # from different working directories don't confuse MLflow about the
        # artifact location.
        mlruns_base = Path(__file__).parent.parent / 'mlruns'
        if not mlruns_base.exists():
            try:
                mlruns_base.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                raise PermissionError(
                    f"Unable to create '{mlruns_base}': {e}\n"
                    "Check the ownership/permissions of the project directory."
                )
        if not os.access(mlruns_base, os.W_OK):
            print(f"WARNING: '{mlruns_base}' is not writable by the current user.")
            print("Please run something like:\n  sudo chown -R $(id -u):$(id -g) {mlruns_base}\n")

        # Limpar o diretório antes do MLflow salvar (MLflow exige diretório vazio)
        if exported.exists():
            shutil.rmtree(exported)
        exported.mkdir(parents=True, exist_ok=True)
        # Salvar o modelo usando MLflow
        mlflow.sklearn.save_model(sk_model=pipe, path=exported)
        print(f'Model saved to: {exported}')

        # clean up any stray directories under mlruns which are not valid
        # experiments; these typically arise when the artifact location has
        # been misconfigured to point at ``mlruns/artifacts``.  The file
        # store's ``search_experiments`` will log warnings for every such
        # folder and later operations (logging a model) may try to treat the
        # directory as an experiment, resulting in MissingConfigException.
        # Removing non-numeric children resets the store to a clean state.
        for child in mlruns_base.iterdir():
            if child.is_dir() and not child.name.isdigit():
                try:
                    shutil.rmtree(child)
                    print(f"Removed extraneous mlruns subdirectory: {child}")
                except Exception:
                    pass

        # determine tracking URI: if the user supplied one use it, otherwise
        # default to a local file-based store under ``mlruns_base``.  note
        # that we deliberately do *not* set a default ``MLFLOW_ARTIFACT_URI``
        # when the tracking URI is file-based; the MLflow file store already
        # places artifacts in ``<mlruns>/experiment-id/artifacts``.  earlier
        # versions of this script forced artifacts into
        # ``mlruns/artifacts`` which caused the corruption seen in the
        # traceback referenced by the user.
        tracking_uri = os.getenv('MLFLOW_TRACKING_URI')
        if not tracking_uri:
            tracking_uri = f"file://{mlruns_base.resolve()}"
        experiment_name = os.getenv('MLFLOW_EXPERIMENT_NAME', 'My Experiment')

        # configure tracking client and ensure experiment artifact location
        mlflow.set_tracking_uri(uri=tracking_uri)
        # attempt to construct a client; if the tracking URI is unreachable we
        # simply skip MLflow logging rather than crashing the entire script.
        client = None
        try:
            client = mlflow.tracking.MlflowClient()
        except Exception as exc:  # includes ConnectionError, MlflowException, etc.
            print(f"WARNING: unable to connect to MLflow tracking server at '{tracking_uri}': {exc}")
            print("Proceeding without MLflow logging.")

        if client is not None:
            # only specify an artifact location when the user has explicitly
            # provided one via environment; if absent we let the tracking
            # store pick the default (which for a file store is
            # ``<mlruns>/<exp_id>/artifacts``).
            desired_artifact_loc = os.environ.get('MLFLOW_ARTIFACT_URI')

            existing_exp = client.get_experiment_by_name(experiment_name)
            if existing_exp is None:
                if desired_artifact_loc:
                    client.create_experiment(
                        name=experiment_name,
                        artifact_location=desired_artifact_loc,
                    )
                    print(
                        f"Created experiment '{experiment_name}' with artifact_location {desired_artifact_loc}"
                    )
                else:
                    client.create_experiment(name=experiment_name)
                    print(f"Created experiment '{experiment_name}'")
            else:
                if desired_artifact_loc and existing_exp.artifact_location != desired_artifact_loc:
                    print(
                        "WARNING: existing experiment '" + experiment_name +
                        "' has artifact_location '" + existing_exp.artifact_location +
                        "', which does not match desired '" + desired_artifact_loc +
                        "'. Creating a new experiment instead."
                    )
                    experiment_name = f"{experiment_name}-{uuid.uuid4().hex}"
                    client.create_experiment(
                        name=experiment_name,
                        artifact_location=desired_artifact_loc,
                    )
                    print(
                        f"Created experiment '{experiment_name}' with artifact_location {desired_artifact_loc}"
                    )
                # otherwise artifact location matches or isn't specified
            mlflow.set_experiment(experiment_name=experiment_name)

        print(f'MLflow tracking URI: {tracking_uri}')
        if 'desired_artifact_loc' in locals():
            print(f"MLflow artifact URI: {desired_artifact_loc}")
        print(f'MLflow experiment name: {experiment_name}')

        # Iniciar uma nova execução no MLflow e logar os parâmetros, métricas e o modelo
        try:
            with mlflow.start_run(run_name=os.getenv('MLFLOW_RUN_NAME', 'train')):
                for key, value in config.items():
                    mlflow.log_param(key=key, value=value)
                for key, value in metrics.items():
                    mlflow.log_metric(key=key, value=value)
                try:
                    mlflow.sklearn.log_model(sk_model=pipe, name='model')
                    # The model has already been saved to `exported` earlier; no need to
                    # call save_model again here (would fail if directory is non-empty).
                    print(f'Model logged to MLflow and available at: {exported}')
                except Exception as log_err:
                    # Catch any problem during logging (including missing
                    # meta.yaml, permission errors, etc.) and continue.
                    print("WARNING: failed to log model to MLflow:", log_err)
        except PermissionError as e:
            raise PermissionError(
                f"MLflow failed to write artifacts due to permission error: {e}\n"
                "Please ensure the 'mlruns' directory is owned by your user.\n"
                "For example: sudo chown -R $(id -u):$(id -g) mlruns"
            )
    else:
        print('MLflow is not installed. Skipping MLflow logging.')
# return pipeline and metrics so callers can inspect results
    return pipe, metrics

import uuid
import tempfile
import shutil

def train_model():
    """Programmatic entry point for training, returns (pipe, metrics).

    The normal ``main()`` implementation writes to a project-local
    ``mlruns`` directory and (by default) uses ``MLFLOW_TRACKING_URI``
    pointing to localhost.  This is convenient for end users but leads to
    flaky tests when previous runs have left behind partially initialized
    experiments (missing ``meta.yaml``) or when the tracking server
    isn't running.  To make the helper safe for automated test suites we
    create a *temporary* file-based tracking store and a random experiment
    name for every invocation.
    """
    # preserve any existing environment configuration so it can be restored
    old_name = os.environ.get('MLFLOW_EXPERIMENT_NAME')
    old_uri = os.environ.get('MLFLOW_TRACKING_URI')

    # create a fresh temp directory and configure MLflow to use it
    temp_dir = tempfile.mkdtemp(prefix="test-mlruns-")
    os.environ['MLFLOW_TRACKING_URI'] = f"file://{temp_dir}"
    os.environ['MLFLOW_EXPERIMENT_NAME'] = f"test-{uuid.uuid4()}"

    try:
        return main()
    finally:
        # restore environment variables
        if old_name is None:
            os.environ.pop('MLFLOW_EXPERIMENT_NAME', None)
        else:
            os.environ['MLFLOW_EXPERIMENT_NAME'] = old_name
        if old_uri is None:
            os.environ.pop('MLFLOW_TRACKING_URI', None)
        else:
            os.environ['MLFLOW_TRACKING_URI'] = old_uri
        # clean up the temporary mlruns directory
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


# Executar a função principal quando o script for executado diretamente
if __name__ == '__main__':
    main()