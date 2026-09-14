from collections.abc import Generator
from pathlib import Path
from typing import BinaryIO

import pytest

from mjml import (
    Include,
    IncludePolicy,
    MJMLValidationErrors,
    ValidationLevel,
    ValidationRule,
    mjml_to_html,
    validate,
)


@pytest.fixture(params=['mjml', 'html', 'css'])
def template_with_invalid_utf8_include(
    request: pytest.FixtureRequest,
    tmp_path: Path,
) -> Generator[tuple[BinaryIO, Path, Path], None, None]:
    invalid = tmp_path / 'invalid.bin'
    invalid.write_bytes(b'\xff')
    include_type = '' if request.param == 'mjml' else f' type="{request.param}"'
    wrapper = tmp_path / 'wrapper.mjml'
    wrapper.write_text(
        '<mjml>\n'
          f'<mj-body><mj-include path="invalid.bin"{include_type} />'
            '<mj-section /></mj-body>\n'
        '</mjml>'
    )
    template = tmp_path / 'template.mjml'
    template.write_text(
        '<mjml>\n'
          '<mj-body><mj-include path="wrapper.mjml" /></mj-body>\n'
        '</mjml>'
    )
    with template.open('rb') as mjml_fp:
        yield mjml_fp, wrapper, template


def test_included_file_may_have_several_root_elements(tmp_path: Path):
    mjml_str = '<mjml><mj-body><mj-include path="./part.mjml" /></mj-body></mjml>'
    included_mjml = (
        '<mj-section><mj-column><mj-text>one</mj-text></mj-column></mj-section>'
        '<mj-section><mj-column><mj-text>two</mj-text></mj-column></mj-section>'
    )

    html = _render(tmp_path, mjml_str, part=included_mjml)
    assert '>one<' in html
    assert '>two<' in html


def test_include_inside_mj_attributes_contributes_nothing(tmp_path: Path):
    # mjml js ignores this mjml
    mjml_str = (
        '<mjml>'
          '<mj-head>'
            '<mj-attributes>'
              '<mj-include path="./part.mjml" />'
            '</mj-attributes>'
          '</mj-head>'
          '<mj-body>'
            '<mj-section>'
              '<mj-column>'
                '<mj-text>t</mj-text>'
              '</mj-column>'
            '</mj-section>'
          '</mj-body>'
        '</mjml>'
    )
    included_mjml = '<mj-attributes><mj-text color="red" /></mj-attributes>'

    html = _render(tmp_path, mjml_str, part=included_mjml)
    assert 'color:red' not in html


def test_rejects_include_directly_inside_mjml(tmp_path: Path):
    # mjml js rejects it too, with "Malformed MJML"
    mjml_str = '<mjml><mj-include path="./part.mjml" /></mjml>'
    included_mjml = '<mjml><mj-body><mj-section><mj-column /></mj-section></mj-body></mjml>'

    with pytest.raises(ValueError):
        _render(tmp_path, mjml_str, part=included_mjml)


def _render(tmp_path: Path, template, **parts) -> str:
    for name, content in parts.items():
        (tmp_path / f'{name}.mjml').write_text(content)
    path = tmp_path / 'template.mjml'
    path.write_text(template)
    with path.open('rb') as mjml_fp:
        return mjml_to_html(mjml_fp, includes=IncludePolicy(roots=[tmp_path])).html


@pytest.mark.parametrize('include', ['<mj-include />', '<mj-include path="" />'])
@pytest.mark.parametrize('level', ['skip', 'soft'])
def test_renders_without_an_include_which_has_no_path(tmp_path: Path, include: str, level: str):
    source = f'<mjml><mj-body>{include}<mj-section /></mj-body></mjml>'
    includes = IncludePolicy(roots=[tmp_path])

    result = mjml_to_html(source, template_dir=tmp_path, validation_level=level, includes=includes)

    assert '<table' in result.html
    assert [error.rule for error in result.errors] == [ValidationRule.INCLUDE_ERROR]


@pytest.mark.parametrize('include', ['<mj-include />', '<mj-include path="" />'])
def test_missing_include_paths_are_validation_errors(tmp_path: Path, include: str):
    source = f'<mjml><mj-body>{include}<mj-section /></mj-body></mjml>'
    includes = IncludePolicy(roots=[tmp_path])

    (error,) = validate(source, template_dir=tmp_path, includes=includes)
    assert error.rule is ValidationRule.INCLUDE_ERROR
    with pytest.raises(MJMLValidationErrors):
        mjml_to_html(source, template_dir=tmp_path, validation_level='strict', includes=includes)


@pytest.mark.parametrize('level', ValidationLevel)
def test_reports_an_include_without_a_parseable_root(tmp_path: Path, level: ValidationLevel):
    (tmp_path / 'part.mjml').write_text('<!-- <mjml> -->')
    source = (
        '<mjml><mj-body><mj-include path="part.mjml" />'
        '<mj-section /></mj-body></mjml>'
    )
    includes = IncludePolicy(roots=[tmp_path])

    (error,) = validate(source, template_dir=tmp_path, includes=includes)
    assert error.rule is ValidationRule.INCLUDE_ERROR
    assert 'contains no mjml' in error.message
    render = lambda: mjml_to_html(
        source, template_dir=tmp_path, validation_level=level, includes=includes
    )
    if level is ValidationLevel.STRICT:
        with pytest.raises(MJMLValidationErrors, match='contains no mjml'):
            render()
    else:
        # the rest of the template still renders
        assert '<table' in render().html


def test_invalid_utf8_include_is_a_validation_error(template_with_invalid_utf8_include):
    mjml_fp, wrapper, template = template_with_invalid_utf8_include
    includes = IncludePolicy(roots=[template.parent])

    (error,) = validate(mjml_fp, includes=includes)

    assert_invalid_utf8_error(error, wrapper, template)


@pytest.mark.parametrize('level', [ValidationLevel.SKIP, ValidationLevel.SOFT])
def test_invalid_utf8_include_does_not_abort_rendering(
    template_with_invalid_utf8_include,
    level: ValidationLevel,
):
    mjml_fp, wrapper, template = template_with_invalid_utf8_include
    includes = IncludePolicy(roots=[template.parent])

    result = mjml_to_html(mjml_fp, validation_level=level, includes=includes)

    assert '<table' in result.html
    assert '<!-- mj-include fails to read file : invalid.bin' in result.html
    (error,) = result.errors
    assert_invalid_utf8_error(error, wrapper, template)


def test_invalid_utf8_include_raises_a_validation_error_in_strict_mode(
    template_with_invalid_utf8_include,
):
    mjml_fp, wrapper, template = template_with_invalid_utf8_include
    includes = IncludePolicy(roots=[template.parent])

    with pytest.raises(MJMLValidationErrors) as exc_info:
        mjml_to_html(mjml_fp, validation_level='strict', includes=includes)

    (error,) = exc_info.value.errors
    assert_invalid_utf8_error(error, wrapper, template)


def assert_invalid_utf8_error(error, wrapper: Path, template: Path) -> None:
    assert error.rule is ValidationRule.INCLUDE_ERROR
    assert 'could not decode' in error.message
    assert 'as UTF-8' in error.message
    assert error.file == str(wrapper)
    assert error.line == 2
    assert error.included_in == (Include(file=str(template), line=2),)
