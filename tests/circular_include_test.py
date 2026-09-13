from pathlib import Path

import pytest

from mjml import IncludePolicy, MJMLValidationErrors, ParseResult, ValidationRule, mjml_to_html


def test_reports_file_including_itself(tmp_path: Path):
    template = tmp_path / 'self.mjml'
    mjml_str = '<mjml><mj-body><mj-include path="./self.mjml" /></mj-body></mjml>'
    template.write_text(mjml_str)

    (error,) = _render(template).errors

    assert error.rule is ValidationRule.INCLUDE_ERROR
    assert 'Circular inclusion' in error.message
    assert str(template) in error.message


def test_reports_cycle_through_another_file(tmp_path: Path):
    (tmp_path / 'a.mjml').write_text('<mj-include path="./b.mjml" />')
    (tmp_path / 'b.mjml').write_text('<mj-include path="./a.mjml" />')
    template = tmp_path / 'template.mjml'
    mjml_str = '<mjml><mj-body><mj-include path="./a.mjml" /></mj-body></mjml>'
    template.write_text(mjml_str)

    (error,) = _render(template).errors
    assert 'Circular inclusion' in error.message
    with template.open('rb') as mjml_fp, pytest.raises(MJMLValidationErrors):
        mjml_to_html(mjml_fp, validation_level='strict', includes=IncludePolicy())


def test_reports_same_file_may_be_included_twice_side_by_side(tmp_path: Path):
    (tmp_path / 'part.mjml').write_text('<mj-section><mj-column /></mj-section>')
    template = tmp_path / 'template.mjml'
    template.write_text(
        '<mjml><mj-body>'
        '<mj-include path="./part.mjml" /><mj-include path="./part.mjml" />'
        '</mj-body></mjml>'
    )

    # should work, not a cycle
    result = _render(template)
    assert result.errors == []
    assert result.html.count('<td') >= 2


def _render(path: Path) -> ParseResult:
    with path.open('rb') as mjml_fp:
        return mjml_to_html(mjml_fp, includes=IncludePolicy())
