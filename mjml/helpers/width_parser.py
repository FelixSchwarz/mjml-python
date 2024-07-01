import re
import typing as t

from .py_utils import strip_unit


__all__ = ['widthParser']


class WidthUnit(t.NamedTuple):
    width: int
    unit: str = "px"

    @property
    def parsedWidth(self):
        return self.width

    def __str__(self):
        return f'{self.width}{self.unit}'


def widthParser(width: str, parseFloatToInt: bool=True) -> WidthUnit:
    pattern = re.compile(r'[\d\.\,]+(?P<unit>\D*)$')

    width_str = str(width)

    if (match := pattern.search(width_str)) is None:
        raise ValueError(f"invalid width '{width}'")

    if (unit := match.groupdict().get("unit")) is None:
        raise RuntimeError("something went wrong...")

    if not isinstance(unit, str):
        raise TypeError(f"invalid unit '{unit}' ({type(unit)})")

    parser = float if (unit == '%') and not parseFloatToInt else int

    # TODO: the value returned from `strip_unit` is already an integer...
    clean_width = strip_unit(width_str)
    parsed_width = parser(clean_width)

    # NOTE: only relevant if we're parsing as float, and the value is an integer
    numerator, denominator = parsed_width.as_integer_ratio()

    if denominator == 1:
        parsed_width = numerator

    if not unit:
        return WidthUnit(width=parsed_width)

    return WidthUnit(width=parsed_width, unit=unit)
