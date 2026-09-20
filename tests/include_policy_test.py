from collections.abc import Generator
from pathlib import Path
from typing import BinaryIO

import pytest

from mjml import (
    IncludePolicy,
    MJMLIncludeError,
    Severity,
    ValidationRule,
    mjml_to_html,
    validate,
)


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
def test_disabled_include_is_fatal_under_every_level(
    template_with_include_inside: BinaryIO,
    level: str
):
    with pytest.raises(MJMLIncludeError) as exc_info:
        mjml_to_html(template_with_include_inside, validation_level=level)

    (error,) = exc_info.value.errors
    assert error.rule is ValidationRule.INCLUDE_DISABLED
    assert error.severity is Severity.ERROR
    assert error.tag_name == 'mj-include'
    assert error.line == 1


def test_validate_reports_a_disabled_include(template_with_include_inside: BinaryIO):
    mjml_fp = template_with_include_inside

    (warning,) = validate(mjml_fp)

    assert warning.rule is ValidationRule.INCLUDE_DISABLED


def test_disabled_include_is_not_looked_at(monkeypatch: pytest.MonkeyPatch):
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

    errors = validate(source)

    assert [error.rule for error in errors] == [ValidationRule.INCLUDE_DISABLED] * 6


def test_include_policy_enables_includes(template_with_include_inside: BinaryIO, tmp_path: Path):
    mjml_fp = template_with_include_inside

    result = mjml_to_html(mjml_fp, includes=IncludePolicy(roots=[tmp_path]))

    assert 'included' in result.html
    assert result.errors == []
