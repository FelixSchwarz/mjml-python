from json import load as json_load

import pytest
from bs4 import BeautifulSoup
from htmlcompare import assert_same_html

from mjml import mjml_to_html
from mjml.testing_helpers import get_mjml_fp, load_expected_html


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
    'mj-html-attributes',
    'mj-column-with-attributes',
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
    'mj-preview',
    'mj-raw',
    'mj-raw-with-tags',
    'mj-raw-head',
    'mj-raw-head-with-tags',
    'mj-social',
    'mj-spacer',
    'mj-text-escaped-html', # this test is security-critical
    'mj-wrapper',
)

@pytest.mark.parametrize('test_id', TEST_IDS)
def test_ensure_same_html_as_upstream(test_id):
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


# The dynamically generated menu key prevents us from just using
# test_ensure_same_html to test mj-navbar
def test_mj_navbar():
    test_id = 'mj-navbar'
    expected_html = load_expected_html(test_id)
    with get_mjml_fp(test_id) as mjml_fp:
        result = mjml_to_html(mjml_fp)

    assert not result.errors
    expected_soup = BeautifulSoup(expected_html, 'html.parser')
    actual_soup = BeautifulSoup(result.html, 'html.parser')

    # This key is randomly generated, so we need to manually replace it.
    menuKey = actual_soup.find(attrs={'class': 'mj-menu-checkbox'})['id']
    expected_soup.find(attrs={'class': 'mj-menu-checkbox'})['id'] = menuKey
    expected_soup.find(attrs={'class': 'mj-menu-label'})['for'] = menuKey

    assert_same_html(str(expected_soup), str(actual_soup), verbose=True)


# The dynamically generated carousel ID prevents us from just using
# test_ensure_same_html to test mj-carousel
def test_mj_carousel():
    test_id = 'mj-carousel'
    expected_html = load_expected_html(test_id)
    with get_mjml_fp(test_id) as mjml_fp:
        result = mjml_to_html(mjml_fp)

    assert not result.errors
    expected_soup = BeautifulSoup(expected_html, 'html.parser')
    actual_soup = BeautifulSoup(result.html, 'html.parser')

    # This ID is randomly generated, so we need to manually replace it.
    def _replace_random_radio_class(soup):
        _mj_cr_str = 'mj-carousel-radio'
        return soup.find(attrs={'class': _mj_cr_str})['name'].replace(f'{_mj_cr_str}-', '')
    expected_carousel_id = _replace_random_radio_class(expected_soup)
    actual_carousel_id = _replace_random_radio_class(actual_soup)
    actual_html = str(actual_soup).replace(actual_carousel_id, expected_carousel_id)
    assert_same_html(str(expected_soup), actual_html, verbose=True)


# htmlcompare is currently unable to detect these kind of
# whitespace differences.
def test_keep_whitespace_before_tag():
    test_id = 'missing-whitespace-before-tag'
    expected_html = load_expected_html(test_id)
    with get_mjml_fp(test_id) as mjml_fp:
        result = mjml_to_html(mjml_fp)

    assert not result.errors
    expected_text = BeautifulSoup(expected_html, 'html.parser').body.get_text().strip()
    body_actual = BeautifulSoup(result.html, 'html.parser').body
    actual_text = body_actual.get_text().strip()
    assert (expected_text == actual_text)
    actual_html = (body_actual.select('.mj-column-per-100 div')[0]).encode_contents()
    assert (b'foo <b>bar</b>.' == actual_html)
