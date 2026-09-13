import re
from pathlib import Path

import pytest

from mjml.scripts.mjml import main


INVALID_MJML = (
    '<mjml>\n'
      '  <mj-body>\n'
        '    <mj-section>\n'
          '      <mj-column>'
            '<mj-text nonexistent="1">hi</mj-text>'
          '</mj-column>\n'
        '    </mj-section>\n'
      '  </mj-body>\n'
    '</mjml>'
)
VALID_MJML = re.sub(r'\s*nonexistent="1"', '', INVALID_MJML)


@pytest.fixture
def template_with_discarded_denial(tmp_path: Path) -> str:
    templates = tmp_path / 'templates'
    templates.mkdir()
    (templates / 'part.mjml').write_text('<mj-section />')
    main_mjml = (
        '<mjml>'
          '<mj-body>'
            '<mj-include path="part.mjml">'
              '<mj-include path="/denied" />'
            '</mj-include>'
          '</mj-body>'
        '</mjml>'
    )
    return _template(templates, main_mjml)


def test_validate_exits_nonzero_and_writes_no_html(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    exit_code = _run_cli(monkeypatch, '--validate', _template(tmp_path, INVALID_MJML))

    assert exit_code == 1
    captured = capsys.readouterr()
    assert 'Attribute nonexistent is illegal' in captured.err
    assert captured.out == ''


def _template(tmp_path: Path, content: str) -> str:
    path = tmp_path / 'template.mjml'
    path.write_text(content)
    return str(path)


def _run_cli(monkeypatch: pytest.MonkeyPatch, *args: str) -> int:
    monkeypatch.setattr('sys.argv', ['mjml', *args])
    try:
        main()
    except SystemExit as exit_error:
        if exit_error.code is None:
            return 0
        if isinstance(exit_error.code, int):
            return exit_error.code
        return 1
    return 0


def test_validate_exits_zero_for_a_valid_template(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    exit_code = _run_cli(monkeypatch, '--validate', _template(tmp_path, VALID_MJML))

    assert exit_code == 0
    assert capsys.readouterr().err == ''


def test_soft_reports_and_still_writes_html(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    out_path = tmp_path / 'out.html'
    exit_code = _run_cli(
        monkeypatch,
        '--validation-level=soft',
        _template(tmp_path, INVALID_MJML),
        '-o',
        str(out_path),
    )

    assert exit_code == 0
    assert 'Attribute nonexistent is illegal' in capsys.readouterr().err
    assert '<html' in out_path.read_text()


def test_strict_exits_nonzero_and_writes_no_html(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    out_path = tmp_path / 'out.html'
    exit_code = _run_cli(
        monkeypatch,
        '--validation-level=strict',
        _template(tmp_path, INVALID_MJML),
        '-o',
        str(out_path),
    )

    assert exit_code == 1
    assert not out_path.exists()


def test_includes_are_disabled_by_default_with_a_hint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    exit_code = _run_cli(monkeypatch, _template_with_include(tmp_path))

    assert exit_code == 0
    captured = capsys.readouterr()
    assert 'included' not in captured.out
    assert 'mj-include is disabled' in captured.err
    assert '--allow-includes' in captured.err


def test_allow_includes_enables_includes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    exit_code = _run_cli(monkeypatch, '--allow-includes', _template_with_include(tmp_path))

    assert exit_code == 0
    captured = capsys.readouterr()
    assert 'included' in captured.out
    assert captured.err == ''


def test_denied_include_renders_a_comment_and_warns_by_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    template = _template_with_include(tmp_path, '../part.mjml')

    exit_code = _run_cli(monkeypatch, '--allow-includes', template)

    assert exit_code == 0
    captured = capsys.readouterr()
    assert '<!-- mj-include denied -->' in captured.out
    assert 'included' not in captured.out
    assert 'was denied' in captured.err


def test_include_denied_error_refuses_to_render(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    template = _template_with_include(tmp_path, '../part.mjml')
    out_path = tmp_path / 'out.html'
    out_path.write_text('previous output')

    exit_code = _run_cli(
        monkeypatch, '--allow-includes', '--include-denied=error', template, '-o', str(out_path),
    )

    assert exit_code == 1
    captured = capsys.readouterr()
    assert captured.out == ''
    assert 'was denied' in captured.err
    assert 'Traceback' not in captured.err
    # a refused rendering must not touch the requested output
    assert out_path.read_text() == 'previous output'


def test_discarded_fatal_denial_does_not_truncate_existing_output(
    tmp_path: Path,
    template_with_discarded_denial: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    template = template_with_discarded_denial
    out_path = tmp_path / 'out.html'
    out_path.write_text('previous output')

    exit_code = _run_cli(
        monkeypatch, '--allow-includes', '--include-denied=error', template, '-o', str(out_path),
    )

    assert exit_code == 1
    captured = capsys.readouterr()
    assert captured.out == ''
    assert 'was denied' in captured.err
    assert out_path.read_text() == 'previous output'


def test_include_path_allows_a_further_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    template = _template_with_include(tmp_path, '../part.mjml')

    exit_code = _run_cli(
        monkeypatch, '--allow-includes', f'--include-path={tmp_path}', template,
    )

    assert exit_code == 0
    captured = capsys.readouterr()
    assert 'included' in captured.out
    assert captured.err == ''


def test_include_path_is_repeatable_and_relative_to_the_working_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    template = _template_with_include(tmp_path, '../part.mjml')
    (tmp_path / 'other').mkdir()
    monkeypatch.chdir(tmp_path)

    exit_code = _run_cli(
        monkeypatch, '--allow-includes', '--include-path=other', '--include-path=.', template,
    )

    assert exit_code == 0
    assert 'included' in capsys.readouterr().out


@pytest.mark.parametrize('args', [
    ('--include-path=.',),
    ('--include-denied=error',),
    ('--allow-includes', '--include-denied=explode'),
    ('--allow-includes', '--include-path=nowhere'),
])
def test_include_options_are_checked(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    args: tuple,
):
    template = _template_with_include(tmp_path)

    exit_code = _run_cli(monkeypatch, *args, template)

    assert exit_code == 1
    captured = capsys.readouterr()
    assert captured.out == ''
    assert 'include' in captured.err


def test_validate_reports_a_denied_include(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    template = _template_with_include(tmp_path, '../part.mjml')

    exit_code = _run_cli(monkeypatch, '--validate', '--allow-includes', template)

    assert exit_code == 1
    assert 'was denied' in capsys.readouterr().err


def test_soft_validation_is_enabled_by_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    out_path = tmp_path / 'out.html'
    exit_code = _run_cli(monkeypatch, _template(tmp_path, INVALID_MJML), '-o', str(out_path))

    assert exit_code == 0
    assert 'Attribute nonexistent is illegal' in capsys.readouterr().err
    assert '<html' in out_path.read_text()


def _template_with_include(tmp_path: Path, include_path: str = './part.mjml') -> str:
    """The template in "templates/", a part next to it and one outside of it."""
    included_mjml = '<mj-section><mj-column><mj-text>included</mj-text></mj-column></mj-section>'
    templates = tmp_path / 'templates'
    templates.mkdir(exist_ok=True)
    (tmp_path / 'part.mjml').write_text(included_mjml)
    (templates / 'part.mjml').write_text(included_mjml)
    path = templates / 'template.mjml'
    main_mjml = (
        '<mjml>'
          '<mj-body>'
            f'<mj-include path="{include_path}" />'
          '</mj-body>'
        '</mjml>'
    )
    path.write_text(main_mjml)
    return str(path)
