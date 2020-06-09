
import re

from .py_utils import strip_unit
from ..lib import AttrDict


__all__ = ['widthParser']

unitRegex = re.compile('[\d.,]*(\D*)$')

def widthParser(width, parseFloatToInt=True):
    width_str = str(width)
    match = unitRegex.search(width_str)
    widthUnit = match.group(1)
    if (widthUnit == '%') and not parseFloatToInt:
        parser = float
    else:
        parser = int
    width = strip_unit(width_str)
    parsed_width = parser(width)
    # LATER: somehow JS works differently here (as it does not have a strict
    # type sytem). parseFloat() might return a number without fractional but
    # python does.
    width_int = int(width)
    if parsed_width == width_int:
        parsed_width = width_int
    return AttrDict(
        parsedWidth = parsed_width,
        unit = widthUnit or 'px',
    )

