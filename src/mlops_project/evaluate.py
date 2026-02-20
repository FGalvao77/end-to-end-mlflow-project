from pathlib import Path


def evaluate_model() -> dict:
    """Load the saved metrics file and return a dictionary of metrics.

    This function assumes the training script has written a text file at
    ``artifacts/metrics/metrics.txt`` containing lines like ``accuracy: 0.95``.
    """
    # Locate metrics file relative to project root
    # deploy.py -> mlops_project -> src -> project_root
    project_root = Path(__file__).resolve().parent.parent.parent
    metrics_file = project_root / 'artifacts' / 'metrics' / 'metrics.txt'
    
    if not metrics_file.exists():
        # Fallback for local execution if path structure differs
        metrics_file = Path('artifacts/metrics/metrics.txt').resolve()

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
