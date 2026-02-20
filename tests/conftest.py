import os
import sys

# ensure src package is importable for tests
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)
