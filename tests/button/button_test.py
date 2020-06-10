
from pathlib import Path
from unittest import TestCase

from htmlcompare import assert_same_html

from mjml import mjml_to_html


THIS_DIR = Path(__file__).parent



class ButtonTest(TestCase):
    def test_ensure_same_html(self):
        with (THIS_DIR / 'button-expected.html').open('rb') as fp:
            expected_html = fp.read()

        mjml_fp = (THIS_DIR / 'button.mjml').open('rb')
        result = mjml_to_html(mjml_fp)
        assert not result.errors
        actual_html = result.html

        assert_same_html(expected_html, actual_html)

