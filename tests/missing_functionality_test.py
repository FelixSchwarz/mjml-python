
from pathlib import Path

import pytest
from htmlcompare import assert_same_html

from mjml import mjml_to_html


TESTDATA_DIR = Path(__file__).parent / 'missing_functionality'

TEST_IDS = (
    'mj-accordion-font-padding',
    'mj-column-border-radius',
    'mj-column-inner-background-color',
    'mj-divider-alignment',
    'mj-divider-width',
    'mj-hero',
    'mj-hero-background-color',
    'mj-hero-background-height',
    'mj-hero-background-position',
    'mj-hero-background-url',
    'mj-hero-background-width',
    'mj-hero-class',
    'mj-hero-divider',
    'mj-hero-height',
    'mj-hero-mode',
    'mj-hero-vertical-align',
    'mj-hero-width',
    'mj-raw',
    'mj-section-background-url-full',
    'mj-section-border-radius',
    'mj-section-full-width-background-url',
    'mj-social-container-background-color',
    'mj-social-share-url',
    'mj-text-height',
    'mj-wrapper-background',
    'mj-wrapper-border',
    'mj-wrapper-full-width-section-background',
)
@pytest.mark.parametrize('test_id', TEST_IDS)
@pytest.mark.xfail
def test_missing_functionality(test_id):
    mjml_filename = f'{test_id}.mjml'
    html_filename = f'{test_id}-expected.html'
    html_path = TESTDATA_DIR / html_filename
    expected_html = html_path.read_text()

    with (TESTDATA_DIR / mjml_filename).open('rb') as mjml_fp:
        result = mjml_to_html(mjml_fp)

    assert not result.errors
    actual_html = result.html
    assert_same_html(expected_html, actual_html, verbose=True)
