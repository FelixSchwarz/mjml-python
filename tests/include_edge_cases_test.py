from pathlib import Path

import pytest

from mjml import mjml_to_html


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
