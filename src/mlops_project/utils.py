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

    # attempt to open the file directly; if it's not found and the path is
    # not absolute, look for it alongside this module (i.e. inside the
    # mlops_project package).  This helps when callers run from the project
    # root or another working directory without adjusting cwd.
    try:
        with open(file=file_path, mode='r', encoding='utf-8') as file:
            config = yaml.safe_load(stream=file)
    except FileNotFoundError:
        fp = Path(file_path)
        if not fp.is_absolute():
            alt = Path(__file__).parent / fp
            with open(file=alt, mode='r', encoding='utf-8') as file:
                config = yaml.safe_load(stream=file)
        else:
            # re-raise original error if absolute path failed
            raise
    
    if config is None:
        config = default
    
    return config   
