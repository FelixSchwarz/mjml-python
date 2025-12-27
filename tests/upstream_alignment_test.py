import random
from json import load as json_load

import pytest
from htmlcompare import assert_same_html

from mjml import mjml_to_html
from mjml.testing_helpers import get_mjml_fp, load_expected_html


@pytest.fixture
def fixed_random_seed():
    state = random.getstate()
    random.seed(42)
    try:
        yield
    finally:
        random.setstate(state)


TEST_IDS = (
    'minimal',
    'hello-world',
    'html-entities',
    'html-without-closing-tag',
    'button',
    'text_with_html',
    'mj-body-with-background-color',
    'mj-breakpoint',
    'mj-title',
    'mj-style',
    'mj-accordion',
    'mj-attributes',
    'mj-attributes-for-mj-body',
    'mj-carousel',
    'mj-html-attributes',
    'mj-column-with-attributes',
    'mj-column-with-fractional-width',
    'mj-group',
    'mj-hero-fixed',
    'mj-hero-fluid',
    'mj-button-with-width',
    'mj-text-with-tail-text',
    'mj-table',
    'mj-head-with-comment',
    'mj-image-with-empty-alt-attribute',
    'mj-image-with-href',
    'mj-section-with-full-width',
    'mj-section-with-css-class',
    'mj-section-with-mj-class',
    'mj-section-with-background-url',
    'mj-section-with-background',
    'mj-font',
    'mj-font-multiple',
    'mj-font-unused',
    'mj-include-body',
    'mj-navbar',
    'mj-preview',
    'mj-raw',
    'mj-raw-with-tags',
    'mj-raw-head',
    'mj-raw-head-with-tags',
    'mj-social',
    'mj-spacer',
    'mj-text-escaped-html', # this test is security-critical
    'mj-wrapper',
    'mjml-lang-attribute',
    'mjml-dir-attribute',
    'missing-whitespace-before-tag',
    'mjml-comment-merging',
)

@pytest.mark.parametrize('test_id', TEST_IDS)
def test_ensure_same_html_as_upstream(test_id, fixed_random_seed):
    expected_html = load_expected_html(test_id)
    with get_mjml_fp(test_id) as mjml_fp:
        result = mjml_to_html(mjml_fp)

    assert not result.errors
    actual_html = result.html
    assert_same_html(expected_html, actual_html, verbose=True)


def test_ensure_same_html_from_json():
    test_id = 'hello-world'
    expected_html = load_expected_html(test_id)
    with get_mjml_fp(test_id, json=True) as mjml_json_fp:
        result = mjml_to_html(json_load(mjml_json_fp))

    assert not result.errors
    actual_html = result.html
    assert_same_html(expected_html, actual_html, verbose=True)


def test_accepts_also_plain_strings_as_input():
    test_id = 'hello-world'
    expected_html = load_expected_html(test_id)
    with get_mjml_fp(test_id) as mjml_fp:
        mjml_str = mjml_fp.read().decode('utf8')
        result = mjml_to_html(mjml_str)

    assert not result.errors
    actual_html = result.html
    assert_same_html(expected_html, actual_html, verbose=True)


@pytest.mark.css_inlining
def test_can_use_css_inlining():
    test_id = 'css-inlining'
    expected_html = load_expected_html(test_id)
    with get_mjml_fp(test_id) as mjml_fp:
        mjml_str = mjml_fp.read().decode('utf8')
        result = mjml_to_html(mjml_str)

    assert not result.errors
    assert_same_html(expected_html, result.html, verbose=True)
