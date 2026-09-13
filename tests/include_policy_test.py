from collections.abc import Generator
from pathlib import Path
from typing import BinaryIO

import pytest

from mjml import IncludePolicy, Severity, ValidationRule, mjml_to_html, validate


@pytest.fixture
def template_with_include_inside(tmp_path: Path) -> Generator[BinaryIO, None, None]:
    included_mjml = '<mj-section><mj-column><mj-text>included</mj-text></mj-column></mj-section>'
    (tmp_path / 'part.mjml').write_text(included_mjml)
    path = tmp_path / 'template.mjml'
    main_mjml = (
        '<mjml>'
          '<mj-body>'
            '<mj-include path="./part.mjml" />'
            '<mj-section>'
              '<mj-column><mj-text>own</mj-text></mj-column>'
            '</mj-section>'
          '</mj-body>'
        '</mjml>'
    )
    path.write_text(main_mjml)
    with path.open('rb') as mjml_fp:
        yield mjml_fp


@pytest.mark.parametrize('level', ['skip', 'soft', 'strict'])
def test_an_include_is_dropped_and_reported_by_default(
    template_with_include_inside: BinaryIO,
    level: str
):
    mjml_fp = template_with_include_inside

    result = mjml_to_html(mjml_fp, validation_level=level)

    assert 'own' in result.html
    assert 'included' not in result.html
    # a warning, so "strict" renders like mjml js does
    (warning,) = result.errors
    assert warning.rule is ValidationRule.INCLUDE_DISABLED
    assert warning.severity is Severity.WARNING
    assert warning.tag_name == 'mj-include'
    assert warning.line == 1


def test_validate_reports_a_disabled_include(template_with_include_inside: BinaryIO):
    mjml_fp = template_with_include_inside

    (warning,) = validate(mjml_fp)

    assert warning.rule is ValidationRule.INCLUDE_DISABLED


def test_a_disabled_include_is_not_looked_at(monkeypatch: pytest.MonkeyPatch):
    def refuse(*args, **kwargs):
        raise AssertionError('the include must not be read')
    monkeypatch.setattr('mjml.parser.resolve_include', refuse)
    monkeypatch.setattr('mjml.parser.include_source', refuse)
    monkeypatch.setattr('mjml.parser.read_include_file', refuse)
    source = (
        '<mjml><mj-body>'
        '<mj-include path="/etc/passwd" type="html" /><mj-include path="/etc/passwd" />'
        '<mj-include path="true" type="html" /><mj-include path="false" type="css" />'
        '<mj-include path="true" /><mj-include path="false" />'
        '<mj-section /></mj-body></mjml>'
    )

    result = mjml_to_html(source)

    assert [error.rule for error in result.errors] == [ValidationRule.INCLUDE_DISABLED] * 6


def test_an_include_policy_enables_includes(template_with_include_inside: BinaryIO):
    mjml_fp = template_with_include_inside

    result = mjml_to_html(mjml_fp, includes=IncludePolicy())

    assert 'included' in result.html
    assert result.errors == []
