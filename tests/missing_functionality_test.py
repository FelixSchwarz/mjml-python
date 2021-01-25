
from pathlib import Path
from unittest import expectedFailure, TestCase

from ddt import ddt as DataDrivenTestCase, data as ddt_data
from htmlcompare import assert_same_html

from mjml import mjml_to_html


TESTDATA_DIR = Path(__file__).parent / 'missing_functionality'

@DataDrivenTestCase
class MissingFeaturesTest(TestCase):
    @ddt_data(
        'html-entities',
    )
    @expectedFailure
    def test_ensure_same_html(self, test_id):
        mjml_filename = f'{test_id}.mjml'
        html_filename = f'{test_id}-expected.html'
        with (TESTDATA_DIR / html_filename).open('rb') as html_fp:
            expected_html = html_fp.read()

        _patch_nose1_result(test=self)
        with (TESTDATA_DIR / mjml_filename).open('rb') as mjml_fp:
            result = mjml_to_html(mjml_fp)

        assert not result.errors
        actual_html = result.html
        assert_same_html(expected_html, actual_html, verbose=True)


def _patch_nose1_result(test):
    # nose's TextTestResult does not support "expected failures" but I still
    # like that test runner. Just treat an expected failure like a skipped test.
    result = test._outcome.result
    if not hasattr(result, 'addExpectedFailure'):
        result.addExpectedFailure = result.addSkip

