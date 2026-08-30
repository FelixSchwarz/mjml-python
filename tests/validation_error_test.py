from io import StringIO

from mjml import ValidationError, ValidationRule, mjml_to_html


def test_valid_template_reports_no_errors():
    mjml = (
        '<mjml>'
        '  <mj-body>'
        '    <mj-section><mj-column><mj-text>text</mj-text></mj-column></mj-section>'
        '  </mj-body>'
        '</mjml>'
    )
    result = mjml_to_html(StringIO(mjml))

    assert result.errors == []


def test_formatted_message_mentions_line_and_file():
    error = _error(line=12, file='/tmp/template.mjml')

    expected = 'Line 12 of /tmp/template.mjml (mj-text) - Attribute foo is illegal'
    assert error.formatted_message() == expected


def test_formatted_message_without_a_file():
    error = _error(line=12)

    assert error.formatted_message() == 'Line 12 (mj-text) - Attribute foo is illegal'


def test_formatted_message_without_a_line():
    # JSON input has no meaningful line numbers
    error = _error(file='/tmp/template.mjml')

    expected = 'File /tmp/template.mjml (mj-text) - Attribute foo is illegal'
    assert error.formatted_message() == expected


def test_formatted_message_without_any_position():
    assert _error().formatted_message() == '(mj-text) - Attribute foo is illegal'


def _error(line=None, file=None):
    return ValidationError(
        message='Attribute foo is illegal',
        tag_name='mj-text',
        rule=ValidationRule.VALID_ATTRIBUTES,
        line=line,
        file=file,
    )
