
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
        'mj-title',
        'mj-style',
        'mj-attributes',
        'mj-group',
        'mj-text-with-tail-text',
        'mj-table',
        'mj-head-with-comment',
        'mj-image-with-empty-alt-attribute',
        'mj-section-with-mj-class',
        'mj-font',
        'mj-font-multiple',
        'mj-font-unused',
        'mj-preview',
        'mj-raw',
        'mj-raw-with-tags',
        'mj-raw-head',
        'mj-raw-head-with-tags',
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
        assert_same_html(expected_html, actual_html, verbose=True)

    @ddt_data('hello-world')
    def test_ensure_same_html_from_json(self, test_id):
        mjml_json_filename = f'{test_id}.mjml.json'
        html_filename = f'{test_id}-expected.html'
        with (TESTDATA_DIR / html_filename).open('rb') as html_fp:
            expected_html = html_fp.read()

        with (TESTDATA_DIR / mjml_json_filename).open('rb') as mjml_json_fp:
            result = mjml_to_html(json_load(mjml_json_fp))

        assert not result.errors
        actual_html = result.html
        assert_same_html(expected_html, actual_html, verbose=True)
