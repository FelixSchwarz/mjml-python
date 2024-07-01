import re
from typing import NamedTuple, Union

from .py_utils import strip_unit


__all__ = ['widthParser']


class WidthUnit(NamedTuple):
    width: Union[int, float]
    unit: str = "px"

    @property
    def parsedWidth(self) -> Union[int, float]:
        return self.width

    def __str__(self) -> str:
        return f'{self.width}{self.unit}'


unitRegex = re.compile(r'[\d.,]*(\D*)$')

def widthParser(width: str, parseFloatToInt: bool=True) -> WidthUnit:
    width_str = str(width)
    match = unitRegex.search(width_str)
    widthUnit = match.group(1) or 'px'

    if (widthUnit == '%') and not parseFloatToInt:
        parsed_width = strip_unit(width_str)
    else:
        parsed_width = int(strip_unit(width_str))

    return WidthUnit(width=parsed_width, unit=widthUnit)
