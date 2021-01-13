
from unittest import TestCase

from mjml.helpers import borderParser



class BorderParserTest(TestCase):
    def test_can_parse_css_none(self):
        self.assertEqual(0, borderParser('none'))

