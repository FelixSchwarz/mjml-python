
import re

from .py_utils import parse_int


__all__ = ['shorthandParser', 'borderParser']

def shorthandParser(cssValue, direction):
    splittedCssValue = cssValue.split(' ')

    top    = 0
    bottom = 0
    left   = 0
    right  = 0
    if len(splittedCssValue) == 2:
        left = 1
        right = 1
    elif len(splittedCssValue) == 3:
        left = 1
        right = 1
        bottom = 2
    elif len(splittedCssValue) == 4:
        right = 1
        bottom = 2
        left = 3
    else:
        return parse_int(cssValue)

    directions = {'top': top, 'bottom': bottom, 'left': left, 'right': right}

    value_int = splittedCssValue[directions[direction]] or 0
    return parse_int(value_int)


def borderParser(border):
    border_regex = re.compile(r'(?:(?:^| )(\d+))')
    match = border_regex.search(border)
    # Upstream does not have to deal with this case as "parseInt(undefined, 10)"
    # does not trigger an exception in JavaScript but just returns NaN.
    # The JS function returns 0 in these cases due to "NaN || 0".
    if match is None:
        return 0
    border_value = match.group(1)
    return parse_int(border_value)
