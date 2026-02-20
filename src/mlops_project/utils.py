from __future__ import annotations
from pathlib import Path
import yaml 

def load_config(file_path:str | Path, default:dict=None) -> dict:
    '''
    Load configuration from a YAML file.
    
    Tries to load the file from the given path. If not found and the path is relative,
    tries to find it relative to the module location.
    
    :param file_path: Path to the YAML configuration file.
    :type file_path: str | Path
    :param default: Default configuration to return if loading fails (optional).
    :type default: dict
    :return: Configuration dictionary.
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
