
from io import StringIO

from mjml import mjml_to_html


def test_can_handle_comments_in_mjml():
    mjml = (
        '<mjml>'
        '  <mj-body>'
        '    <!-- empty -->'
        '  </mj-body>'
        '</mjml>'
    )
    mjml_to_html(StringIO(mjml))
