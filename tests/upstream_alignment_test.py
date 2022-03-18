
from contextlib import contextmanager
from json import load as json_load
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
        'mj-body-with-background-color',
        'mj-title',
        'mj-style',
        'mj-attributes',
        'mj-group',
        'mj-text-with-tail-text',
        'mj-table',
        'mj-head-with-comment',
        'mj-image-with-empty-alt-attribute',
        'mj-image-with-href',
        'mj-section-with-mj-class',
        'mj-section-with-background-url',
        'mj-font',
        'mj-font-multiple',
        'mj-font-unused',
        'mj-include-body',
        'mj-preview',
        'mj-raw',
        'mj-raw-with-tags',
        'mj-raw-head',
        'mj-raw-head-with-tags',
    )
    def test_ensure_same_html(self, test_id):
        expected_html = load_expected_html(test_id)
        with get_mjml_fp(test_id) as mjml_fp:
            result = mjml_to_html(mjml_fp)

        assert not result.errors
        actual_html = result.html
        assert_same_html(expected_html, actual_html, verbose=True)

    @ddt_data('hello-world')
    def test_ensure_same_html_from_json(self, test_id):
        expected_html = load_expected_html(test_id)
        with get_mjml_fp(test_id, json=True) as mjml_json_fp:
            result = mjml_to_html(json_load(mjml_json_fp))

        assert not result.errors
        actual_html = result.html
        assert_same_html(expected_html, actual_html, verbose=True)

    def test_accepts_also_plain_strings_as_input(self):
        test_id = 'hello-world'
        expected_html = load_expected_html(test_id)
        with get_mjml_fp(test_id) as mjml_fp:
            mjml_str = mjml_fp.read().decode('utf8')
            result = mjml_to_html(mjml_str)

        assert not result.errors
        actual_html = result.html
        assert_same_html(expected_html, actual_html, verbose=True)



def load_expected_html(test_id):
    html_filename = f'{test_id}-expected.html'
    with (TESTDATA_DIR / html_filename).open('rb') as html_fp:
        expected_html = html_fp.read()
    return expected_html

@contextmanager
def get_mjml_fp(test_id, json=False):
    mjml_filename = f'{test_id}.mjml'
    if json:
        mjml_filename += '.json'
    with (TESTDATA_DIR / mjml_filename).open('rb') as mjml_fp:
        yield mjml_fp

