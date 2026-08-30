
from mjml.helpers import remove_important_from_inlined_styles


def test_removes_important_from_modified_style_attributes():
    html = '<p style="color:red">foo</p>'
    inlined_html = '<p style="font-weight: bold !important;color: red">foo</p>'

    result = remove_important_from_inlined_styles(html, inlined_html)
    assert result == '<p style="font-weight: bold;color: red">foo</p>'


def test_keeps_important_in_unmodified_style_attributes():
    # the CSS inliner only rewrites the "style" attribute if a CSS rule matched
    # the element - all other attributes must stay as they are.
    html = '<p style="color:red !important; margin:0">foo</p>'

    result = remove_important_from_inlined_styles(html, html)
    assert result == html


def test_removes_important_from_all_declarations():
    html = '<p>foo</p>'
    inlined_html = '<p style="color: red !important;margin: 0 !important">foo</p>'

    result = remove_important_from_inlined_styles(html, inlined_html)
    assert result == '<p style="color: red;margin: 0">foo</p>'


def test_ignores_important_in_the_middle_of_a_value():
    html = '<p>foo</p>'
    inlined_html = '<p style="font-family: !important foo">foo</p>'

    result = remove_important_from_inlined_styles(html, inlined_html)
    assert result == inlined_html
