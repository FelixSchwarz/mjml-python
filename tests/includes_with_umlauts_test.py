
from io import StringIO
from unittest import TestCase

from schwarz.fakefs_helpers import FakeFS

from mjml import mjml_to_html



class IncludesWithUmlautsTest(TestCase):
    def test_can_properly_handle_include_umlauts(self):
        fs = FakeFS.set_up(test=self)
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
        fs.create_file('footer.mjml', contents=included_mjml.encode('utf8'))

        result = mjml_to_html(StringIO(mjml))
        html = result.html

        assert ('äöüß' in html)

