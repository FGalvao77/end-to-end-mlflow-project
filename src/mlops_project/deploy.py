from pathlib import Path


def export_model() -> str:
    """Return the path to a serialized model file in the artifacts directory.

    Looks for either a ``.pkl`` or ``.joblib`` file under
    ``artifacts/model`` and returns the first match.  Raises
    ``FileNotFoundError`` if no exported model exists.
    """
    # locate the artifacts folder relative to this module so that the
    # function behaves the same whether it is called from project root,
    # a test suite, or the script execution directory.
    model_dir = Path(__file__).parent / 'artifacts' / 'model'
    model_dir = model_dir.resolve()
    if not model_dir.is_dir():
        raise FileNotFoundError(f"Model directory not found: {model_dir}")

    for ext in ('*.pkl', '*.joblib'):
        candidates = list(model_dir.glob(ext))
        if candidates:
            return str(candidates[0])

    raise FileNotFoundError(f"No exported model found in {model_dir}")
