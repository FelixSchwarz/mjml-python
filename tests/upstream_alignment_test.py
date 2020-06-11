
from pathlib import Path
from unittest import TestCase

from ddt import ddt as DataDrivenTestCase, data as ddt_data
from htmlcompare import assert_same_html

from mjml import mjml_to_html



TESTDATA_DIR = Path(__file__).parent / 'testdata'

@DataDrivenTestCase
class UpstreamAlignmentTest(TestCase):
    @ddt_data(
        'minimal',
        'hello-world',
        'button',
        'text_with_html',
        'mj-title',
        'mj-style',
    )
    def test_ensure_same_html(self, test_id):
        mjml_filename = f'{test_id}.mjml'
        html_filename = f'{test_id}-expected.html'
        with (TESTDATA_DIR / html_filename).open('rb') as html_fp:
            expected_html = html_fp.read()

        with (TESTDATA_DIR / mjml_filename).open('rb') as mjml_fp:
            result = mjml_to_html(mjml_fp)

        assert not result.errors
        actual_html = result.html
        assert_same_html(expected_html, actual_html)

