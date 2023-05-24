
from pathlib import Path
from unittest import TestCase, expectedFailure

from ddt import data as ddt_data, ddt as DataDrivenTestCase
from htmlcompare import assert_same_html

from mjml import mjml_to_html


TESTDATA_DIR = Path(__file__).parent / 'missing_functionality'

def patch_nose1(func):
    def _wrapper(test, *args, **kwargs):
        _patch_nose1_result(test)
        return func(test, *args, **kwargs)
    return _wrapper


@DataDrivenTestCase
class MissingFeaturesTest(TestCase):
    @ddt_data(
    )
    @expectedFailure
    @patch_nose1
    def test_ensure_same_html(self, test_id):
        mjml_filename = f'{test_id}.mjml'
        html_filename = f'{test_id}-expected.html'
        with (TESTDATA_DIR / html_filename).open('rb') as html_fp:
            expected_html = html_fp.read()

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
    if not hasattr(result, 'addUnexpectedSuccess'):
        def _addUnexpectedSuccess(test):
            error = (AssertionError, AssertionError('unexpected success'), None)
            return result.addFailure(test, error)
        result.addUnexpectedSuccess = _addUnexpectedSuccess
