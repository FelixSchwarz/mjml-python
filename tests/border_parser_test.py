
from mjml.helpers import borderParser


def test_can_parse_css_none():
    assert borderParser('none') == 0
