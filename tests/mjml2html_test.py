
from io import StringIO
from unittest import TestCase

from mjml import mjml_to_html



class MJML2HTMLTest(TestCase):
    def test_can_handle_comments_in_mjml(self):
        mjml = (
            '<mjml>'
            '  <mj-body>'
            '    <!-- empty -->'
            '  </mj-body>'
            '</mjml>'
        )
        mjml_to_html(StringIO(mjml))

