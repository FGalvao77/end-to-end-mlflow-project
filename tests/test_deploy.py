import os
import sys

# ensure package path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from mlops_project import deploy

def test_model_export() -> None:
    path = deploy.export_model()
    assert path.endswith('.pkl') or path.endswith('.joblib')

if __name__ == '__main__':
    test_model_export()
    print('Model export test passed!')
