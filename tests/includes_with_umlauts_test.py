
from io import StringIO

from mjml import IncludePolicy, mjml_to_html


def test_can_properly_handle_include_umlauts(tmp_path):
    included_mjml = (
        '<mj-section>'
        '  <mj-column>'
        '    <mj-text>äöüß</mj-text>'
        '  </mj-column>'
        '</mj-section>'
    )
    mjml = (
        '<mjml>'
        '  <mj-body>'
        '    <mj-text>foo bar</mj-text>'
        '    <mj-include path="./footer.mjml" />'
        '  </mj-body>'
        '</mjml>'
    )
    path_footer = tmp_path / 'footer.mjml'
    path_footer.write_text(included_mjml, encoding='utf8')

    includes = IncludePolicy(roots=[tmp_path])
    result = mjml_to_html(StringIO(mjml), template_dir=tmp_path, includes=includes)
    html = result.html

    assert ('äöüß' in html)
