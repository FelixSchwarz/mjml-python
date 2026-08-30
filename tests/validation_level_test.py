import re
from io import StringIO

import pytest

from mjml import MJMLValidationErrors, ValidationRule, mjml_to_html, validate


INVALID_MJML = """
<mjml>
  <mj-body>
    <mj-section>
      <mj-column>
        <mj-text>Hello World</mj-text>
        <p>bug</p>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
"""

VALID_MJML = re.sub(r'<p>bug</p>', '', INVALID_MJML, flags=re.MULTILINE)


def test_validation_is_skipped_by_default():
    result = mjml_to_html(StringIO(INVALID_MJML))

    assert result.errors == []
    assert 'Hello World' in result.html


def test_soft_reports_errors_and_still_renders():
    result = mjml_to_html(StringIO(INVALID_MJML), validation_level='soft')

    (error,) = result.errors
    assert error.rule is ValidationRule.VALID_TAG
    assert 'Hello World' in result.html


def test_strict_raises_before_rendering():
    with pytest.raises(MJMLValidationErrors) as exc_info:
        mjml_to_html(StringIO(INVALID_MJML), validation_level='strict')

    (error,) = exc_info.value.errors
    assert error.rule is ValidationRule.VALID_TAG
    assert "Element p doesn't exist or is not registered" in str(exc_info.value)


def test_strict_renders_a_valid_template():
    result = mjml_to_html(StringIO(VALID_MJML), validation_level='strict')
    assert 'Hello World' in result.html


def test_skip_and_soft_render_the_same_html():
    skipped = mjml_to_html(StringIO(VALID_MJML), validation_level='skip')
    soft = mjml_to_html(StringIO(VALID_MJML), validation_level='soft')

    assert skipped.html == soft.html
    assert not soft.errors
    assert not skipped.errors


def test_errors_from_json_input_carry_no_position():
    def _node(tag_name: str, children=(), content='', **attrs) -> dict[str, object]:
        return dict(tagName=tag_name, attributes=attrs, children=list(children), content=content)

    template = _node(
        'mjml',
        children=[
            _node(
                'mj-body',
                children=[
                    _node(
                        'mj-section',
                        children=[
                            _node(
                                'mj-column',
                                children=[
                                    _node('mj-text', content='Hello World'),
                                    _node('p', content='bug'),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
    (error,) = validate(template)

    assert error.rule is ValidationRule.VALID_TAG
    # the line would point into the xml we generated internally from the json
    assert error.line is None
    assert error.column is None
