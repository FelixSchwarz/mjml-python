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


def test_validation_is_off_by_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    out_path = tmp_path / 'out.html'
    exit_code = _run_cli(monkeypatch, _template(tmp_path, INVALID_MJML), '-o', str(out_path))

    assert exit_code == 0
    assert capsys.readouterr().err == ''
    assert '<html' in out_path.read_text()
