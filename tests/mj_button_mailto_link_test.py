
from io import StringIO
import re
from unittest import TestCase

import lxml.html

from mjml import mjml_to_html



class MjButtonMailtoLinkTest(TestCase):
    def test_no_target_for_mailto_links(self):
        mjml = (
            '<mjml>'
            '  <mj-body>'
            '    <mj-button href="mailto:foo@site.example">Click me</mj-button>'
            '  </mj-body>'
            '</mjml>'
        )

        result = mjml_to_html(StringIO(mjml))
        html = result.html
        mailto_match = re.search('<a href="([^"]+?)"[^>]*>', html)
        start, end = mailto_match.span()
        match_str = html[start:end]

        a_el = lxml.html.fragment_fromstring(match_str)
        self.assertEqual('mailto:foo@site.example', a_el.attrib['href'])
        target = a_el.attrib.get('target')
        # Thunderbird opens a blank page instead of the new message window if
        # the <a> contains 'target="_blank"'.
        #   https://bugzilla.mozilla.org/show_bug.cgi?id=1677248
        #   https://bugzilla.mozilla.org/show_bug.cgi?id=1589968
        #   https://bugzilla.mozilla.org/show_bug.cgi?id=421310
        assert not target, f'target="{target}"'

