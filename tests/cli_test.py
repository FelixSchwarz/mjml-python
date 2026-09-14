import re
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

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


def test_template_dir_is_rejected_for_a_template_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    exit_code = _run_cli(monkeypatch, '--template-dir=nowhere', _template(tmp_path, VALID_MJML))

    assert exit_code == 1
    captured = capsys.readouterr()
    assert captured.out == ''
    assert '--template-dir applies only to a template read from stdin' in captured.err


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
    assert '--include-path' in captured.err


def test_include_path_enables_includes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    template = _template_with_include(tmp_path)
    templates = tmp_path / 'templates'

    exit_code = _run_cli(monkeypatch, f'--include-path={templates}', template)

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
    templates = tmp_path / 'templates'

    exit_code = _run_cli(monkeypatch, f'--include-path={templates}', template)

    assert exit_code == 0
    captured = capsys.readouterr()
    assert '<!-- mj-include denied -->' in captured.out
    assert 'included' not in captured.out
    assert 'was denied' in captured.err


def test_include_path_allows_files_outside_the_template_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    template = _template_with_include(tmp_path, '../part.mjml')

    exit_code = _run_cli(monkeypatch, f'--include-path={tmp_path}', template)

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

    exit_code = _run_cli(monkeypatch, '--include-path=other', '--include-path=.', template)

    assert exit_code == 0
    assert 'included' in capsys.readouterr().out


def test_include_path_does_not_allow_the_template_directory_implicitly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    template = _template_with_include(tmp_path)
    other = tmp_path / 'other'
    other.mkdir()

    exit_code = _run_cli(monkeypatch, f'--include-path={other}', template)

    assert exit_code == 0
    assert '<!-- mj-include denied -->' in capsys.readouterr().out


@pytest.mark.parametrize(('args', 'message'), [
    (('--include-path=nowhere',), '--include-path "nowhere" is not a directory'),
    (('--include-path=.', '--template-dir=.'),
     '--template-dir applies only to a template read from stdin'),
])
def test_include_options_are_checked(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    args: tuple,
    message: str,
):
    template = _template_with_include(tmp_path)

    exit_code = _run_cli(monkeypatch, *args, template)

    assert exit_code == 1
    captured = capsys.readouterr()
    assert captured.out == ''
    assert message in captured.err


def test_validate_reports_a_denied_include(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    template = _template_with_include(tmp_path, '../part.mjml')
    templates = tmp_path / 'templates'

    exit_code = _run_cli(monkeypatch, '--validate', f'--include-path={templates}', template)

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


def test_stdin_template_needs_a_template_dir_for_includes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    stdin_mjml = b'<mjml><mj-body><mj-include path="part.mjml" /></mj-body></mjml>'
    monkeypatch.setattr('sys.stdin', SimpleNamespace(buffer=BytesIO(stdin_mjml)))

    exit_code = _run_cli(monkeypatch, f'--include-path={tmp_path}', '-')

    assert exit_code == 1
    captured = capsys.readouterr()
    assert captured.out == ''
    assert '--template-dir' in captured.err


@pytest.mark.parametrize(('args', 'message'), [
    (('--template-dir=nowhere', '--include-path=.'), '--template-dir "nowhere" is not a directory'),
    (('--template-dir=.',), '--template-dir needs --include-path'),
])
def test_stdin_template_dir_options_are_checked(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    args: tuple,
    message: str,
):
    stdin_mjml = b'<mjml><mj-body><mj-section /></mj-body></mjml>'
    monkeypatch.setattr('sys.stdin', SimpleNamespace(buffer=BytesIO(stdin_mjml)))

    exit_code = _run_cli(monkeypatch, *args, '-')

    assert exit_code == 1
    captured = capsys.readouterr()
    assert captured.out == ''
    assert message in captured.err


def test_stdin_template_includes_relative_to_the_template_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    template = _template_with_include(tmp_path)
    stdin_mjml = Path(template).read_bytes()
    monkeypatch.setattr('sys.stdin', SimpleNamespace(buffer=BytesIO(stdin_mjml)))
    templates = tmp_path / 'templates'

    exit_code = _run_cli(
        monkeypatch, f'--include-path={templates}', f'--template-dir={templates}', '-',
    )

    assert exit_code == 0
    captured = capsys.readouterr()
    assert 'included' in captured.out
    assert captured.err == ''


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
