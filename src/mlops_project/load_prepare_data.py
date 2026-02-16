from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

def load_data(as_frame:bool=False) -> tuple:
    '''
    Docstring for load_data
    :return: Description of the return value
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
    Docstring for prepare_data
    
    :param X: Description
    :type X: tuple
    :param y: Description
    :type y: tuple
    :param size: Description
    :type size: float
    :param random_state: Description
    :type random_state: int
    :param stratify: Description
    :type stratify: bool
    :return: Description
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