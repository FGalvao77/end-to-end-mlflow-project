from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

def load_data(as_frame:bool=False) -> tuple:
    '''
    Load the Breast Cancer dataset from scikit-learn.
    
    :param as_frame: If True, the data is a pandas DataFrame including columns with appropriate dtypes (numeric).
    :type as_frame: bool
    :return: A tuple containing (data, target).
    :rtype: tuple

    Example:
    >>> X, y = load_data()
    >>> print(X.shape, y.shape)
    (569, 30) (569,)
    '''

    data = load_breast_cancer(as_frame=as_frame)
    '''
    Docstring for data.DESCR
    :return: Description of the return value
    :rtype: str
    '''

    print(f'INFOS: {data.DESCR}')
    '''
     Docstring for data.data
     :return: Description of the return value
     :rtype: numpy.ndarray
    '''

    X = data.data
    y = data.target
    '''
    Docstring for X
        :return: Description of the return value
        :rtype: numpy.ndarray
    '''

    return X, y

def prepare_data(X:tuple, y:tuple, size:float, 
                 random_state:int, stratify:bool) -> tuple:
    '''
    Prepares the dataset by splitting it into training and testing sets.
    
    This function performs a stratified train-test split, ensuring that 
    the class distribution is maintained across the training and testing sets.
    Default values are used if 'None' is provided for size, random_state, or stratify.
    
    :param X: Feature dataset (e.g., pandas DataFrame or numpy array).
    :type X: tuple (or compatible type)
    :param y: Target variable (e.g., pandas Series or numpy array).
    :type y: tuple (or compatible type)
    :param size: Proportion of the dataset to include in the test split (e.g., 0.2 for 20%).
    :type size: float
    :param random_state: Controls the randomness of the data splitting.
    :type random_state: int
    :param stratify: If True, data is split in a stratified fashion using `y` as the class labels.
    :type stratify: bool
    :return: A tuple containing (X_train, X_test, y_train, y_test) datasets.
    :rtype: tuple

    Example:
    >>> X_train, X_test, y_train, y_test = prepare_data(X, y, size=0.2, random_state=42, stratify=True)
    >>> print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)
    (455, 30) (114, 30) (455,) (114,)
    '''

    if size == 'None':
        size = 0.2
    if random_state == 'None':
        random_state = 42
    if stratify == 'None':
        stratify = True
    
    X_train, X_test, y_train, y_test = \
        train_test_split(X, y, 
                         test_size=size,
                         random_state=random_state,
                         stratify=y if stratify else None)
    
    return X_train, X_test, y_train, y_test

# script for testing the functions
# if __name__ == "__main__":
#     X, y = load_data()
#     X_train, X_test, y_train, y_test = \
#         prepare_data(X, y, size=0.2, 
#                      random_state=42, 
#                      stratify=True)
#     print(f'X_train shape: {X_train.shape}, y_train shape: {y_train.shape}')
#     print(f'X_test shape: {X_test.shape}, y_test shape: {y_test.shape}')    