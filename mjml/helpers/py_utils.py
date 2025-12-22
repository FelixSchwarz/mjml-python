
import re
from decimal import Decimal
from typing import Union


__all__ = [
    'is_nil',
    'is_empty',
    'is_not_empty',
    'is_not_nil',
    'omit',
    'parse_float',
    'parse_int',
    'parse_percentage',
    'strip_unit',
]

def omit(attributes, keys):
    if isinstance(keys, str):
        keys = (keys, )
    _attrs = dict(attributes)
    for key in keys:
        if key in _attrs:
            _attrs.pop(key)
    return _attrs

def parse_float(value_str):
    match = re.search(r'^([-+]?\d+(.\d+)?)*', value_str)
    return float(match.group(1))

def parse_int(value_str):
    if isinstance(value_str, int):
        return value_str
    match = re.search(r'^([-+]?\d+)*', value_str)
    return int(match.group(1))

def parse_percentage(value_str):
    match = re.search(r'^(\d+(\.\d+)?)%$', value_str)
    return Decimal(match.group(1))

def strip_unit(value_str: Union[str, int, float]) -> Union[int, float]:
    """
    Extract numeric value from a CSS value string like "600px" or "33.33%".

    Mimics JavaScript parseInt() behavior: returns an integer when the value
    is a whole number, otherwise returns a float.

    Examples:
        strip_unit("600px") → 600
        strip_unit("33.33%") → 33.33
        strip_unit("600.0px") → 600
    """
    match = re.search(r'^(-?\d+(?:\.\d+)?)', str(value_str))
    if not match:
        return 0
    num = float(match.group(1))
    # Return int for whole numbers (like JS parseInt for "600px")
    return int(num) if num == int(num) else num

def is_nil(v):
    return (v is None)

def is_not_nil(v):
    return not is_nil(v)

def is_empty(v):
    if v is None:
        return True
    elif hasattr(v, 'strip'):
        return not bool(v.strip())
    elif isinstance(v, (int, float)):
        # Numeric zero is a valid CSS value (e.g. line-height: 0)
        return False
    return not bool(v)

def is_not_empty(v):
    return not is_empty(v)
