import re
from collections.abc import Mapping
from typing import Any


__all__ = ['formatAttributes']

# js: types/color.js "matcher"
_color_type_regex = re.compile(r'^color')
# js: types/color.js "shorthandRegex"/"replaceInputRegex"
# "re.ASCII" so "\w" matches the same characters as in JavaScript.
_color_shorthand_regex = re.compile(r'^#(\w)(\w)(\w)$', re.ASCII)


def formatAttributes(
    attributes: Mapping[str, Any],
    allowed_attrs: Mapping[str, str],
) -> dict[str, Any]:
    """
    Return the attributes with their values normalized as implied by the
    declared attribute type.

    Only attributes declared as "color" are affected: the shorthand notation
    "#abc" is expanded to "#aabbcc". Other types do not imply a value
    conversion.
    """
    formatted_attrs = {}
    for attr_name, value in attributes.items():
        attr_type = allowed_attrs.get(attr_name)
        if attr_type and _color_type_regex.match(attr_type) and isinstance(value, str):
            value = _color_shorthand_regex.sub(r'#\1\1\2\2\3\3', value)
        formatted_attrs[attr_name] = value
    return formatted_attrs
