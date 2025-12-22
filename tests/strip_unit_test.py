
import pytest

from mjml.helpers import strip_unit


def test_integer_pixel_value():
    value = strip_unit('600px')
    assert isinstance(value, int)
    assert value == 600

def test_fractional_pixel_value():
    value = strip_unit('600.5px')
    assert value == pytest.approx(600.5)

def test_percentage_value():
    assert strip_unit('33.33%') == pytest.approx(33.33)

def test_whole_float_normalized_to_int():
    # 600.0 should become 600 (int), not 600.0 (float)
    value = strip_unit('600.0px')
    assert isinstance(value, int)
    assert value == 600

def test_numeric_string_without_unit():
    assert strip_unit('100') == 100

def test_numeric_input():
    assert strip_unit(600) == 600

def test_negative_value():
    assert strip_unit('-10px') == -10

def test_invalid_input_returns_zero():
    assert strip_unit('abc') == 0
    assert strip_unit('') == 0
