"""
raw-string assertions on the generated html.

The alignment suite compares semantically, so it might not notice when tag
casing, entities or whitespace inside untouched content change.
"""

from mjml import mjml_to_html
from mjml.testing_helpers import get_mjml_fp


def test_escaped_html_stays_escaped():
    # Preserve the original entity spelling; unescaping it into markup would be unsafe.
    html = _render('mj-text-escaped-html')

    assert 'Pretty unsafe: &lt;script&gt;' in html
    assert '<script>' not in html


def test_tags_inside_mj_raw_are_passed_through_verbatim():
    html = _render('mj-raw-with-tags')

    assert '<h1 style="color:red;">Hello World!</h1>' in html
    assert '<!-- Your content goes here -->' in html


def test_css_inside_mj_style_is_not_reformatted():
    html = _render('mj-style')

    assert '.red-text div {' in html
    assert 'color: red !important;' in html


def test_comments_are_kept_verbatim():
    html = _render('mjml-comment-merging')

    assert '<!-- Comment 1 -->' in html
    assert '<!-- Comment 2 -->' in html


def test_comments_can_be_dropped():
    html = _render('mjml-comment-merging', keep_comments=False)

    assert '<!-- Comment 1 -->' not in html


def test_downlevel_revealed_conditional_comment_is_preserved():
    # htmlcompare 0.4.1 treats this marker as a regular comment and ignores it.
    # It must remain intact so non-Outlook clients reveal the enclosed HTML
    # while Outlook recognizes the condition and hides it.
    assert '<!--[if !mso]><!-->' in _render('mj-style')


def _render(test_id: str, **kwargs) -> str:
    with get_mjml_fp(test_id) as mjml_fp:
        return mjml_to_html(mjml_fp, **kwargs).html
