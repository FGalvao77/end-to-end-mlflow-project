# tests/test_data_preprocessing.py
# path manipulation is handled by tests/conftest.py so we can import normally
from mlops_project import data_prep


def test_data_split() -> None:
    # use the data_prep helpers
    X, y = data_prep.load_data(as_frame=False)
    X_train, X_test, y_train, y_test = data_prep.prepare_data(
        X=X, y=y, size=0.2, random_state=42, stratify=True
    )
    assert len(X_train) > 0
    assert len(X_test) > 0
    assert len(y_train) == len(X_train)
    assert len(y_test) == len(X_test)

if __name__ == '__main__':
    test_data_split()
    print('Data preprocessing test passed!')
