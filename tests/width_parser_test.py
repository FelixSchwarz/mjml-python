
import pytest

from mjml.helpers import widthParser


@pytest.mark.parametrize('kwargs', [{'parseFloatToInt': False}, {}])
def test_width_parser_with_full_percentage(kwargs):
    # 100.0 should become 100 (int), not 100.0 (float)
    result = widthParser('100%', **kwargs)
    assert isinstance(result.width, int)
    assert result.width == 100
    assert result.unit == '%'

def test_width_parser_with_fractional_percentage_as_float():
    # JS parseFloat("33.33%") returns 33.33
    result = widthParser('33.33%', parseFloatToInt=False)
    assert result.width == pytest.approx(33.33)
    assert result.unit == '%'

def test_width_parser_with_fractional_percentage_as_int():
    result = widthParser('33.33%', parseFloatToInt=True)
    assert isinstance(result.width, int)
    assert result.width == 33
    assert result.unit == '%'

def test_width_parser_with_integer_pixel_value():
    result = widthParser('100px')
    assert isinstance(result.width, int)
    assert result.width == 100
    assert result.unit == 'px'

def test_width_parser_truncates_fractional_pixel_values_by_default():
    # JS parseInt("33.5px") returns 33
    result = widthParser('33.5px')
    assert isinstance(result.width, int)
    assert result.width == 33
    assert result.unit == 'px'

@pytest.mark.parametrize('input_value', ['100', 100])
def test_width_parser_without_unit_defaults_to_px(input_value):
    result = widthParser(input_value)
    assert isinstance(result.width, int)
    assert result.width == 100
    assert result.unit == 'px'
