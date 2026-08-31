from pathlib import Path

import pytest

from mjml import MJMLValidationErrors, ValidationLevel, ValidationRule, mjml_to_html, validate


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
        return mjml_to_html(mjml_fp).html


@pytest.mark.parametrize('include', ['<mj-include />', '<mj-include path="" />'])
@pytest.mark.parametrize('level', ['skip', 'soft'])
def test_aborts_rendering_on_missing_include_paths(include: str, level: str):
    source = f'<mjml><mj-body>{include}<mj-section /></mj-body></mjml>'

    with pytest.raises(ValueError, match='has no "path" attribute'):
        mjml_to_html(source, validation_level=level)


@pytest.mark.parametrize('include', ['<mj-include />', '<mj-include path="" />'])
def test_missing_include_paths_are_validation_errors(include: str):
    source = f'<mjml><mj-body>{include}<mj-section /></mj-body></mjml>'

    (error,) = validate(source)
    assert error.rule is ValidationRule.INCLUDE_ERROR
    with pytest.raises(MJMLValidationErrors):
        mjml_to_html(source, validation_level='strict')


@pytest.mark.parametrize('level', ValidationLevel)
def test_aborts_rendering_on_include_without_a_parseable_root(
        tmp_path: Path, level: ValidationLevel,
):
    (tmp_path / 'part.mjml').write_text('<!-- <mjml> -->')
    source = (
        '<mjml><mj-body><mj-include path="part.mjml" />'
        '<mj-section /></mj-body></mjml>'
    )

    (error,) = validate(source, template_dir=tmp_path)
    assert error.rule is ValidationRule.INCLUDE_ERROR
    exception = MJMLValidationErrors if level is ValidationLevel.STRICT else ValueError
    with pytest.raises(exception, match='contains no mjml'):
        mjml_to_html(source, template_dir=tmp_path, validation_level=level)
