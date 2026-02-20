# tests/test_train.py
# package import is configured via tests/conftest.py which adds `src` to sys.path
from mlops_project import train

def test_model_training() -> None:
    model, metrics = train.train_model()
    assert model is not None
    assert 'accuracy' in metrics
    assert metrics['accuracy'] > 0.5  # sanity check

if __name__ == '__main__':
    test_model_training()