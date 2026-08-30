from io import StringIO

from mjml import mjml_to_html


def test_unknown_body_element_is_skipped():
    mjml = (
        '<mjml><mj-body><mj-section><mj-column>'
        '<mj-nonexistent>ignored</mj-nonexistent>'
        '<mj-text>text</mj-text>'
        '</mj-column></mj-section></mj-body></mjml>'
    )
    html = mjml_to_html(StringIO(mjml)).html

    assert 'ignored' not in html
    assert 'text' in html


def test_unknown_head_element_is_skipped_with_a_message_on_stderr(capsys):
    mjml = (
        '<mjml><mj-head><mj-nonexistent /></mj-head>'
        '<mj-body><mj-section><mj-column><mj-text>text</mj-text></mj-column></mj-section>'
        '</mj-body></mjml>'
    )
    html = mjml_to_html(StringIO(mjml)).html

    assert 'text' in html
    captured = capsys.readouterr()
    assert captured.err == 'No matching component for tag : mj-nonexistent\n'
    # the cli writes the generated html to stdout
    assert captured.out == ''
