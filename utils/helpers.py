import re
from pathlib import Path

from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Dict,
    List,
    Tuple,
    Type,
    IO
)

if TYPE_CHECKING:
    pass


#print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())


def is_dec(value: str) -> bool:
    """ Check if a string value is a decimal/float value """

    float_match = re.match('^\-?([0-9]+)\.([0-9]+)$', value)

    return float_match is not None

def cast(value: str) -> Any:
    """ Cast a string value to its appropriate data type. """
    
    result = None
    data_type = None

    if type(value) is not str:
        return value

    value = value.strip()

    if value.lower() == 'true': return True
    if value.lower() == 'false': return False
    if value == '': return None
    if value == 'none': return None

    try:
        isdec = is_dec(value)

        if is_dec(value) is True:
            result = float(value)
            data_type = type(result)
            return result
    except:
        pass

    try:
        result = int(value)
        data_type = type(result)
        return result
    except:
        pass

    return value


def get_project_root() -> Path:
    return Path(__file__).parent.parent
