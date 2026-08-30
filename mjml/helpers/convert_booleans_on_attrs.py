from collections.abc import Mapping
from typing import Any


__all__ = ['convertBooleansOnAttrs']


def convertBooleansOnAttrs(attrs: Mapping[str, Any]) -> dict[str, Any]:
    """
    Return the attributes with the exact values "true" and "false" converted
    to booleans.

    An attribute like "fluid-on-mobile" is only meaningful as a boolean:
    without this conversion the string "false" would be true.
    """
    converted_attrs = {}
    for attr_name, value in attrs.items():
        if value == 'true':
            value = True
        elif value == 'false':
            value = False
        converted_attrs[attr_name] = value
    return converted_attrs
