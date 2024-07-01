import re
import typing as t
from decimal import Decimal


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


# TODO typing: figure out types
def omit(attributes, keys):
    if isinstance(keys, str):
        keys = (keys, )
    _attrs = dict(attributes)
    for key in keys:
        if key in _attrs:
            _attrs.pop(key)
    return _attrs

def parse_float(value: str) -> float:
    if (match := re.search(r'^([-+]?\d+(.\d+)?)*', value)) is None:
        raise ValueError(f"could not parse float from '{value}'")
    return float(match.group(1))

def parse_int(value: str) -> int:
    if (match := re.search(r'^([-+]?\d+)*', value)) is None:
        raise ValueError(f"could not parse int from '{value}'")
    return int(match.group(1))

def parse_percentage(value: str) -> Decimal:
    if (match := re.search(r'^(\d+(\.\d+)?)%$', value)) is None:
        raise ValueError(f"could not parse decimal from '{value}'")
    return Decimal(match.group(1))

# TODO: fix if this should support decimals/floats as well
def strip_unit(value: str) -> int:
    if (match := re.search(r'^(\d+).*', value)) is None:
        raise ValueError(f"could not strip unit from '{value}'")
    return int(match.group(1))

def is_nil(v: t.Optional[t.Any]) -> bool:
    return (v is None)

def is_not_nil(v: t.Optional[t.Any]) -> bool:
    return not is_nil(v)

def is_empty(v: t.Optional[t.Sequence[t.Any]]) -> bool:
    if v is None:
        return True
    elif hasattr(v, 'strip'):
        return not bool(v.strip())
    return not bool(v)

def is_not_empty(v: t.Optional[t.Sequence[t.Any]]) -> bool:
    return not is_empty(v)
