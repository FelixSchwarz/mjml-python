from mjml import mjml_to_html


def test_mj_include_with_type_html_is_not_parsed_as_mjml(tmp_path):
    # The included HTML must be injected verbatim. Previously its children were
    # handed to the component registry which raised "KeyError: 'div'".
    (tmp_path / 'snippet.html').write_text(
        '<div class="raw"><p>a &amp; b</p></div>', encoding='utf8')
    mjml = (
        '<mjml>'
        '  <mj-body>'
        '    <mj-section><mj-column>'
        '      <mj-include path="./snippet.html" type="html" />'
        '    </mj-column></mj-section>'
        '  </mj-body>'
        '</mjml>'
    )
    path_mjml = tmp_path / 'email.mjml'
    path_mjml.write_text(mjml, encoding='utf8')

    with path_mjml.open('rb') as mjml_fp:
        html = mjml_to_html(mjml_fp).html

    assert '<div class="raw"><p>a &amp; b</p></div>' in html


def test_mj_include_with_type_html_resolves_path_relative_to_including_file(tmp_path):
    partials = tmp_path / 'partials'
    partials.mkdir()
    (partials / 'snippet.html').write_text('<span class="deep">deep</span>', encoding='utf8')
    (partials / 'wrapper.mjml').write_text(
        '<mj-section><mj-column>'
        '  <mj-include path="./snippet.html" type="html" />'
        '</mj-column></mj-section>',
        encoding='utf8',
    )
    mjml = (
        '<mjml>'
        '  <mj-body>'
        '    <mj-include path="./partials/wrapper.mjml" />'
        '  </mj-body>'
        '</mjml>'
    )
    path_mjml = tmp_path / 'email.mjml'
    path_mjml.write_text(mjml, encoding='utf8')

    with path_mjml.open('rb') as mjml_fp:
        html = mjml_to_html(mjml_fp).html

    assert '<span class="deep">deep</span>' in html
