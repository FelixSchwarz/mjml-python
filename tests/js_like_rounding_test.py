import pytest

from mjml.elements.mj_column import js_like_rounding


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        (-2.51, -3),
        (-2.5, -2),
        (-2.49, -2),
        (-0.5, 0),
        (-0.49, 0),
        (0.49, 0),
        (0.5, 1),
        (2.5, 3),
    ],
)
def test_js_like_rounding(value, expected):
    assert js_like_rounding(value) == expected


def test_js_like_rounding_accepts_numeric_strings():
    assert js_like_rounding('2.5') == 3
