
import re


__all__ = [
    'is_nil',
    'is_empty',
    'is_not_empty',
    'is_not_nil',
    'omit',
    'parse_float',
    'parse_int',
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
    match = re.search('^([-+]?\d+(.\d+)?)*', value_str)
    return float(match.group(1))

def parse_int(value_str):
    if isinstance(value_str, int):
        return value_str
    match = re.search('^([-+]?\d+)*', value_str)
    return int(match.group(1))

def strip_unit(value_str):
    match = re.search('^(\d+).*', value_str)
    return int(match.group(1))

def is_nil(v):
    return (v is None)

def is_not_nil(v):
    return not is_nil(v)

def is_empty(v):
    if v is None:
        return True
    elif hasattr(v, 'strip'):
        return not bool(v.strip())
    return not bool(v)

def is_not_empty(v):
    return not is_empty(v)

