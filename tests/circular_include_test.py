from pathlib import Path

import pytest

from mjml import mjml_to_html
from mjml.helpers import CircularIncludeError


def test_reports_file_including_itself(tmp_path: Path):
    template = tmp_path / 'self.mjml'
    mjml_str = '<mjml><mj-body><mj-include path="./self.mjml" /></mj-body></mjml>'
    template.write_text(mjml_str)

    with pytest.raises(CircularIncludeError) as exc_info:
        _render(template)

    assert str(template) in str(exc_info.value)


def test_reports_cycle_through_another_file(tmp_path: Path):
    (tmp_path / 'a.mjml').write_text('<mj-include path="./b.mjml" />')
    (tmp_path / 'b.mjml').write_text('<mj-include path="./a.mjml" />')
    template = tmp_path / 'template.mjml'
    mjml_str = '<mjml><mj-body><mj-include path="./a.mjml" /></mj-body></mjml>'
    template.write_text(mjml_str)

    with pytest.raises(CircularIncludeError):
        _render(template)


def test_reports_same_file_may_be_included_twice_side_by_side(tmp_path: Path):
    (tmp_path / 'part.mjml').write_text('<mj-section><mj-column /></mj-section>')
    template = tmp_path / 'template.mjml'
    template.write_text(
        '<mjml><mj-body>'
        '<mj-include path="./part.mjml" /><mj-include path="./part.mjml" />'
        '</mj-body></mjml>'
    )

    # should work, not a cycle
    assert _render(template).count('<td') >= 2


def _render(path: Path) -> str:
    with path.open('rb') as mjml_fp:
        return mjml_to_html(mjml_fp).html
