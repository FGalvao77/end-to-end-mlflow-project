from pathlib import Path


def export_model() -> str:
    """Return the path to a serialized model file in the artifacts directory.

    Looks for either a ``.pkl`` or ``.joblib`` file under
    ``artifacts/model`` and returns the first match.  Raises
    ``FileNotFoundError`` if no exported model exists.
    """
    # locate the artifacts folder relative to the project root.
    # Assuming the structure is:
    # project_root/
    #   artifacts/
    #   src/
    #     mlops_project/
    #       deploy.py
    #
    # We go up 3 levels: deploy.py -> mlops_project -> src -> project_root
    project_root = Path(__file__).resolve().parent.parent.parent
    model_dir = project_root / 'artifacts' / 'model'
    
    if not model_dir.is_dir():
        # Fallback: try local directory if running from root without package structure assumption
        # or if artifacts are placed differently.
        model_dir = Path('artifacts/model').resolve()

    if not model_dir.is_dir():
        raise FileNotFoundError(f"Model directory not found at: {model_dir}")

    for ext in ('*.pkl', '*.joblib'):
        candidates = list(model_dir.glob(ext))
        if candidates:
            return str(candidates[0])

    raise FileNotFoundError(f"No exported model found in {model_dir}")
