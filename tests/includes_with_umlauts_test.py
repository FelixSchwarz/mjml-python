
import os
from contextlib import contextmanager
from io import StringIO

from mjml import mjml_to_html


# could use "contextlib.chdir" in Python 3.11+
# https://github.com/python/cpython/commit/3592980f9122ab0d9ed93711347742d110b749c2
@contextmanager
def chdir(path):
    old_chdir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(old_chdir)


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

    with chdir(tmp_path):
        result = mjml_to_html(StringIO(mjml))
    html = result.html

    assert ('äöüß' in html)
