
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


def _mjml_with_column(root_attrs=''):
    return (
        f'<mjml{root_attrs}>'
        '  <mj-body>'
        '    <mj-section>'
        '      <mj-column><mj-text>text</mj-text></mj-column>'
        '    </mj-section>'
        '  </mj-body>'
        '</mjml>'
    )


def test_printer_support_repeats_the_media_queries_for_printing():
    html = mjml_to_html(StringIO(_mjml_with_column()), printer_support=True).html

    assert '@media only print {' in html
    print_style = html.split('@media only print {')[1].split('</style>')[0]
    assert '.mj-column-per-100 { width:100% !important; max-width: 100%; }' in print_style


def test_printer_support_is_disabled_by_default():
    html = mjml_to_html(StringIO(_mjml_with_column())).html

    assert '@media only print' not in html


def test_printer_support_style_precedes_the_owa_style():
    # upstream emits the "@media only print" block before the "[owa] " one.
    mjml = _mjml_with_column(root_attrs=' owa="desktop"')
    html = mjml_to_html(StringIO(mjml), printer_support=True).html

    assert '[owa] ' in html
    assert html.index('@media only print') < html.index('[owa] ')


def test_mj_class_with_boolean_like_value_does_not_break_rendering():
    # The parser converts "true" and "false" to booleans. `mj-class` requires a
    # string containing class names, so a boolean value must not break rendering.
    mjml_str = (
        '<mjml>'
          '<mj-body>'
            '<mj-section>'
              '<mj-column>'
                '<mj-text mj-class="true">text</mj-text>'
              '</mj-column>'
            '</mj-section>'
        '</mj-body></mjml>'
    )
    assert 'text' in mjml_to_html(StringIO(mjml_str)).html
