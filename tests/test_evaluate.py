import os
import sys

# ensure package path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from mlops_project import evaluate

def test_model_evaluation() -> None:
    results = evaluate.evaluate_model()
    assert isinstance(results, dict)
    assert 'accuracy' in results
    assert 0.0 <= results['accuracy'] <= 1.0

if __name__ == '__main__':
    test_model_evaluation()
    print('Model evaluation test passed!')
