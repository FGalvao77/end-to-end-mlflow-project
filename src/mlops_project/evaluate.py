from pathlib import Path


def evaluate_model() -> dict:
    """Load the saved metrics file and return a dictionary of metrics.

    This function assumes the training script has written a text file at
    ``artifacts/metrics/metrics.txt`` containing lines like ``accuracy: 0.95``.
    """
    # path relative to this module's directory (src/mlops_project)
    metrics_file = Path(__file__).parent / 'artifacts' / 'metrics' / 'metrics.txt'
    metrics_file = metrics_file.resolve()
    if not metrics_file.exists():
        raise FileNotFoundError(f"Metrics file not found: {metrics_file}")

    metrics: dict = {}
    with open(metrics_file, 'r') as f:
        for line in f:
            if ':' in line:
                key, value = line.strip().split(':', 1)
                key = key.strip()
                try:
                    metrics[key] = float(value)
                except ValueError:
                    metrics[key] = value.strip()
    return metrics
