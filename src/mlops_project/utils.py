from __future__ import annotations
from pathlib import Path
import yaml 

def load_config(file_path:str | Path, default:dict=None) -> dict:
    '''
    Docstring for load_config
    
    :param file_path: Description
    :type file_path: str | Path
    :param default: Description
    :type default: dict
    :return: Description
    :rtype: dict

    Example:
    >>> config = load_config('config.yaml')
    >>> print(config)
    {'param1': 'value1', 'param2': 'value2'}
    '''

    with open(file=file_path, mode='r', encoding='utf-8') as file:
        config = yaml.safe_load(stream=file)
    
    if config is None:
        config = default
    
    return config   
