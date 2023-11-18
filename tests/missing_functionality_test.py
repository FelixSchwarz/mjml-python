
from pathlib import Path

import pytest
from htmlcompare import assert_same_html

from mjml import mjml_to_html


TESTDATA_DIR = Path(__file__).parent / 'missing_functionality'

# currently there are no tests which are expected to fail
@pytest.mark.parametrize('test_id', [])
@pytest.mark.xfail
def test_missing_functionality(test_id):
    mjml_filename = f'{test_id}.mjml'
    html_filename = f'{test_id}-expected.html'
    with (TESTDATA_DIR / html_filename).open('rb') as html_fp:
        expected_html = html_fp.read()

    with (TESTDATA_DIR / mjml_filename).open('rb') as mjml_fp:
        result = mjml_to_html(mjml_fp)

    assert not result.errors
    actual_html = result.html
    assert_same_html(expected_html, actual_html, verbose=True)
