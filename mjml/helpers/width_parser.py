
import re
from collections import namedtuple

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


unitRegex = re.compile(r'[\d.,]*(\D*)$')

def widthParser(width, parseFloatToInt=True):
    width_str = str(width)
    match = unitRegex.search(width_str)
    widthUnit = match.group(1)

    if (widthUnit == '%') and not parseFloatToInt:
        parsed_width = strip_unit(width_str)
    else:
        parsed_width = int(strip_unit(width_str))

    return WidthUnit(width=parsed_width, unit=widthUnit)
