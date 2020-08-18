
from collections import namedtuple
import re

from .py_utils import strip_unit


__all__ = ['widthParser']

_WidthUnit = namedtuple('_WidthUnit', ('width', 'unit'))

class WidthUnit(_WidthUnit):
    def __new__(cls, width, *, unit='px'):
        if not unit:
            unit = 'px'
        return super().__new__(cls, width=width, unit=unit)

    @property
    def parsedWidth(self):
        return self.width

    def __str__(self):
        return f'{self.width}{self.unit}'


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

    return WidthUnit(width=parsed_width, unit=widthUnit)

