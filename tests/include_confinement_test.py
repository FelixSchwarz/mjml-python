import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import pytest

from mjml import (
    Include,
    IncludeAccessError,
    IncludeDenied,
    IncludePolicy,
    Severity,
    ValidationRule,
    mjml_to_html,
    validate,
)


DENIED = '<!-- mj-include denied -->'
PART = '<mj-section><mj-column><mj-text>PART</mj-text></mj-column></mj-section>'
SECRET = '<mj-section><mj-column><mj-text>SECRET</mj-text></mj-column></mj-section>'


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """"templates" holds the template, "secret.mjml" lies next to it."""
    templates = tmp_path / 'templates'
    (templates / 'sub').mkdir(parents=True)
    (templates / 'part.mjml').write_text(PART)
    (templates / 'sub' / 'deep.mjml').write_text(PART)
    (tmp_path / 'secret.mjml').write_text(SECRET)
    (tmp_path / 'secret.html').write_text('<b>SECRET</b>')
    (tmp_path / 'secret.css').write_text('.secret { color: red; }')
    return templates


@pytest.fixture
def discarded_denial_templates(tmp_path: Path):
    ok = tmp_path / 'ok.mjml'
    ok.write_text('<mj-section />')
    replaced = tmp_path / 'replaced.mjml'
    replaced.write_text(
        '<mjml>\n'
          '<mj-body>\n'
            '<mj-include path="ok.mjml">\n'
              '<mj-include path="/denied" />\n'
            '</mj-include>\n'
          '</mj-body>\n'
        '</mjml>'
    )

    two_bodies_part = tmp_path / 'two-bodies-part.mjml'
    two_bodies_part.write_text(
        '<mjml>\n'
          '<mj-body><mj-section /></mj-body>\n'
          '<mj-body><mj-include path="/denied" /></mj-body>\n'
        '</mjml>'
    )
    two_bodies = tmp_path / 'two-bodies.mjml'
    two_bodies.write_text(
        '<mjml>\n'
          '<mj-body><mj-include path="two-bodies-part.mjml" /></mj-body>\n'
        '</mjml>'
    )

    before_root = tmp_path / 'before-root.mjml'
    before_root.write_text(
        '<mj-include path="/denied" />\n'
        '<mjml><mj-body><mj-section /></mj-body></mjml>'
    )

    return [
        ('replaced include children', replaced, replaced, 4, ()),
        (
            'second included body',
            two_bodies,
            two_bodies_part,
            3,
            (Include(file=str(two_bodies), line=2),),
        ),
        ('markup before root', before_root, before_root, 1, ()),
    ]


# --- allowed ---

def test_sibling_file_may_be_included(tree: Path):
    result = _render(_template(tree, '<mj-include path="./part.mjml" />'))

    assert 'PART' in result.html
    assert result.errors == []


def test_parent_reference_which_stays_inside_the_root_is_allowed(tree: Path):
    result = _render(_template(tree, '<mj-include path="sub/../part.mjml" />'))

    assert 'PART' in result.html
    assert result.errors == []


def test_symlink_inside_the_root_is_allowed(tree: Path):
    (tree / 'link.mjml').symlink_to(tree / 'part.mjml')

    result = _render(_template(tree, '<mj-include path="link.mjml" />'))

    assert 'PART' in result.html


def test_nested_include_may_reach_the_parent_directory_inside_the_root(tree: Path):
    (tree / 'sub' / 'deep.mjml').write_text('<mj-include path="../part.mjml" />')

    result = _render(_template(tree, '<mj-include path="sub/deep.mjml" />'))

    assert 'PART' in result.html
    assert result.errors == []


def test_in_memory_template_includes_relative_to_the_working_directory(
    tree: Path, monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.chdir(tree)

    result = mjml_to_html(
        '<mjml><mj-body><mj-include path="part.mjml" /></mj-body></mjml>',
        includes=IncludePolicy(),
    )

    assert 'PART' in result.html


@pytest.mark.parametrize('path_value', ['true', 'false'])
@pytest.mark.parametrize(
    ('include_type', 'content'),
    [
        ('mjml', '<mj-section><mj-column><mj-text>BOOLEAN_PATH</mj-text></mj-column></mj-section>'),
        ('html', '<b>BOOLEAN_PATH</b>'),
        ('css', '.BOOLEAN_PATH { color: red; }'),
    ],
)
def test_boolean_like_include_paths_name_literal_files(
    tree: Path,
    path_value: str,
    include_type: str,
    content: str,
):
    (tree / path_value).write_text(content)
    type_attribute = '' if include_type == 'mjml' else f' type="{include_type}"'
    path = _template(tree, f'<mj-include path="{path_value}"{type_attribute} />')

    with path.open('rb') as mjml_fp:
        validation_errors = validate(mjml_fp, includes=IncludePolicy())
    result = _render(path)

    assert validation_errors == []
    assert result.errors == []
    assert 'BOOLEAN_PATH' in result.html


# --- denied ---

def test_parent_reference_leaving_the_root_is_denied(tree: Path):
    result = _render(_template(tree, '<mj-include path="../secret.mjml" />'))

    assert_denied(result, 'below the allowed directories')


@pytest.mark.parametrize('path', [
    'ABSOLUTE',
    'C:/secret.mjml',
    'c:\\secret.mjml',
    '\\secret.mjml',
    '//host/share/secret.mjml',
    '\\\\host\\share\\secret.mjml',
])
def test_absolute_and_windows_paths_are_denied(tree: Path, path: str, tmp_path: Path):
    if path == 'ABSOLUTE':
        path = str(tmp_path / 'secret.mjml')
    result = _render(_template(tree, f'<mj-include path="{path}" />'))

    assert_denied(result, 'absolute')


@pytest.mark.parametrize('path_value', ['part%20', 'part%2e', 'part%25', 'part%00'])
@pytest.mark.parametrize(
    ('include_type', 'content'),
    [
        ('mjml', '<mj-section><mj-column><mj-text>PERCENT_PATH</mj-text></mj-column></mj-section>'),
        ('html', '<b>PERCENT_PATH</b>'),
        ('css', '.PERCENT_PATH { color: red; }'),
    ],
)
def test_percent_escapes_are_literal_in_all_include_types(
    tree: Path,
    path_value: str,
    include_type: str,
    content: str,
):
    (tree / path_value).write_text(content)
    type_attribute = '' if include_type == 'mjml' else f' type="{include_type}"'

    result = _render(_template(tree, f'<mj-include path="{path_value}"{type_attribute} />'))

    assert 'PERCENT_PATH' in result.html
    assert result.errors == []


def test_percent_escape_names_a_different_file_than_a_space(tree: Path):
    (tree / 'part%20one.mjml').write_text(PART)
    (tree / 'part one.mjml').write_text(SECRET)

    result = _render(_template(tree, '<mj-include path="part%20one.mjml" />'))

    assert 'PART' in result.html
    assert 'SECRET' not in result.html


def test_spaces_unicode_and_markup_entities_in_include_paths(tree: Path):
    (tree / 'résumé & final.mjml').write_text(PART)

    result = _render(_template(tree, '<mj-include path="résumé &amp; final.mjml" />'))

    assert 'PART' in result.html
    assert result.errors == []


@pytest.mark.parametrize(
    ('include_type', 'content'),
    [
        (
            'mjml',
            '<mj-section><mj-column>'
              '<mj-text>NESTED_PERCENT</mj-text>'
            '</mj-column></mj-section>',
        ),
        ('html', '<b>NESTED_PERCENT</b>'),
        ('css', '.NESTED_PERCENT { color: red; }'),
    ],
)
def test_nested_percent_escapes_are_literal(
    tree: Path,
    include_type: str,
    content: str,
):
    type_attribute = '' if include_type == 'mjml' else f' type="{include_type}"'
    (tree / 'part%2520').write_text(content)
    (tree / 'part%20').write_text(content.replace('NESTED_PERCENT', 'WRONG_FILE'))
    (tree / 'outer%2520.mjml').write_text(
        f'<mj-include path="part%2520"{type_attribute} />'
    )
    (tree / 'outer%20.mjml').write_text('<mj-section css-class="WRONG_FILE" />')

    result = _render(_template(tree, '<mj-include path="outer%2520.mjml" />'))

    assert 'NESTED_PERCENT' in result.html
    assert 'WRONG_FILE' not in result.html
    assert result.errors == []


def test_raw_nul_byte_is_denied(tmp_path: Path):
    source = '<mjml><mj-body><mj-include path="part\x00.mjml" /></mj-body></mjml>'

    result = mjml_to_html(source, template_dir=tmp_path, includes=IncludePolicy())

    assert_denied(result, 'NUL')


def test_percent_encoded_traversal_is_a_missing_literal_target(tree: Path):
    result = _render(_template(tree, '<mj-include path="%2e%2e/secret.mjml" />'))

    assert_denied(result, 'below the allowed directories')


def test_percent_encoded_traversal_may_name_a_literal_directory(tree: Path):
    (tree / '%2e%2e').mkdir()
    (tree / '%2e%2e' / 'secret.mjml').write_text(PART)

    result = _render(_template(tree, '<mj-include path="%2e%2e/secret.mjml" />'))

    assert 'PART' in result.html
    assert 'SECRET' not in result.html
    assert result.errors == []


def test_literal_percent_encoded_traversal_symlink_outside_is_denied(
    tree: Path,
    tmp_path: Path,
):
    (tree / '%2e%2e').symlink_to(tmp_path)

    result = _render(_template(tree, '<mj-include path="%2e%2e/secret.mjml" />'))

    assert_denied(result, 'below the allowed directories')


def test_symlink_pointing_out_of_the_root_is_denied(tree: Path, tmp_path: Path):
    (tree / 'link.mjml').symlink_to(tmp_path / 'secret.mjml')

    result = _render(_template(tree, '<mj-include path="link.mjml" />'))

    assert_denied(result, 'below the allowed directories')

    # the message would otherwise tell where the link points
    assert str(tmp_path / 'secret.mjml') not in result.errors[0].message


def test_missing_and_existing_targets_outside_the_root_are_denied_alike(tree: Path):
    existing = _render(_template(tree, '<mj-include path="../secret.mjml" />'))
    missing = _render(_template(tree, '<mj-include path="../nowhere.mjml" />'))

    (existing_error,) = existing.errors
    (missing_error,) = missing.errors
    assert existing_error.message.replace('secret', 'nowhere') == missing_error.message


def test_broken_symlink_is_denied(tree: Path):
    (tree / 'link.mjml').symlink_to(tree / 'nowhere.mjml')

    result = _render(_template(tree, '<mj-include path="link.mjml" />'))

    assert_denied(result, 'below the allowed directories')


def test_symlink_loop_is_denied_without_an_exception(tree: Path):
    (tree / 'loop.mjml').symlink_to(tree / 'loop.mjml')
    path = _template(tree, '<mj-include path="loop.mjml" />')

    assert_denied(_render(path), 'below the allowed directories')
    with path.open('rb') as mjml_fp:
        (error,) = validate(mjml_fp, includes=IncludePolicy())
    assert error.rule is ValidationRule.INCLUDE_DENIED


def test_missing_target_is_denied_as_in_mjml_js(tree: Path):
    result = _render(_template(tree, '<mj-include path="missing.mjml" />'))

    assert_denied(result, 'below the allowed directories')


@pytest.mark.parametrize('path_value', ['true', 'false'])
@pytest.mark.parametrize('include_type', ['mjml', 'html', 'css'])
def test_missing_boolean_like_include_path_is_an_ordinary_denial(
    tree: Path,
    path_value: str,
    include_type: str,
):
    type_attribute = '' if include_type == 'mjml' else f' type="{include_type}"'
    path = _template(tree, f'<mj-include path="{path_value}"{type_attribute} />')

    with path.open('rb') as mjml_fp:
        (validation_error,) = validate(mjml_fp, includes=IncludePolicy())
    result = _render(path)

    assert validation_error.rule is ValidationRule.INCLUDE_DENIED
    assert f'"{path_value}"' in validation_error.message
    assert_denied(result, 'below the allowed directories')


def test_nested_include_may_not_leave_the_root(tree: Path):
    (tree / 'sub' / 'deep.mjml').write_text('<mj-include path="../../secret.mjml" />')

    result = _render(_template(tree, '<mj-include path="sub/deep.mjml" />'))

    assert_denied(result, 'below the allowed directories')
    (error,) = result.errors
    assert error.file == str(tree / 'sub' / 'deep.mjml')


@pytest.mark.parametrize('include', [
    '<mj-include path="../secret.html" type="html" />',
    '<mj-include path="../secret.css" type="css" />',
])
def test_html_and_css_includes_obey_the_policy(tree: Path, include: str):
    result = _render(_template(tree, include))

    assert 'SECRET' not in result.html
    assert 'secret' not in result.html
    (error,) = result.errors
    assert error.rule is ValidationRule.INCLUDE_DENIED


# --- roots ---

def test_additional_root_allows_its_files(tree: Path, tmp_path: Path):
    shared = tmp_path / 'shared'
    shared.mkdir()
    (shared / 'footer.mjml').write_text(PART)
    policy = IncludePolicy(roots=[shared])

    result = _render(_template(tree, '<mj-include path="../shared/footer.mjml" />'), policy)

    assert 'PART' in result.html
    assert result.errors == []


@pytest.mark.parametrize(
    ('include_type', 'content'),
    [
        (
            'mjml',
            '<mj-section><mj-column>'
              '<mj-text>EXTRA_PERCENT</mj-text>'
            '</mj-column></mj-section>',
        ),
        ('html', '<b>EXTRA_PERCENT</b>'),
        ('css', '.EXTRA_PERCENT { color: red; }'),
    ],
)
def test_percent_escapes_are_literal_in_an_additional_root(
    tree: Path,
    tmp_path: Path,
    include_type: str,
    content: str,
):
    shared = tmp_path / 'shared'
    shared.mkdir()
    (shared / 'footer%20final').write_text(content)
    (shared / 'footer final').write_text(content.replace('EXTRA_PERCENT', 'WRONG_FILE'))
    policy = IncludePolicy(roots=[shared])
    type_attribute = '' if include_type == 'mjml' else f' type="{include_type}"'

    result = _render(
        _template(
            tree,
            f'<mj-include path="../shared/footer%20final"{type_attribute} />',
        ),
        policy,
    )

    assert 'EXTRA_PERCENT' in result.html
    assert 'WRONG_FILE' not in result.html
    assert result.errors == []


def test_single_root_may_be_given_as_a_string(tmp_path: Path):
    policy = IncludePolicy(roots=str(tmp_path))

    assert policy.roots == (str(tmp_path),)


def test_relative_root_is_resolved_against_the_working_directory(
    tree: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.chdir(tmp_path)
    policy = IncludePolicy(roots=['.'])

    result = _render(_template(tree, '<mj-include path="../secret.mjml" />'), policy)

    assert 'SECRET' in result.html


def test_missing_root_is_rejected_before_anything_is_read(tree: Path, tmp_path: Path):
    path = _template(tree, '<mj-include path="part.mjml" />')

    with pytest.raises(ValueError, match='does not exist'):
        _render(path, IncludePolicy(roots=[tmp_path / 'nowhere']))
    with pytest.raises(ValueError, match='not a directory'):
        _render(path, IncludePolicy(roots=[tmp_path / 'secret.mjml']))


# --- response to a denial ---

@pytest.mark.parametrize('level', ['skip', 'soft', 'strict'])
def test_denial_renders_the_comment_and_warns_under_every_level(tree: Path, level: str):
    result = _render(
        _template(tree, '<mj-include path="../secret.mjml" />'), validation_level=level
    )

    assert_denied(result)


@pytest.mark.parametrize('level', ['skip', 'soft', 'strict'])
def test_error_mode_raises_before_rendering_under_every_level(tree: Path, level: str):
    path = _template(tree, '<mj-include path="../secret.mjml" />')
    policy = IncludePolicy(on_denied=IncludeDenied.ERROR)

    with pytest.raises(IncludeAccessError) as exc_info:
        _render(path, policy, validation_level=level)

    (error,) = exc_info.value.errors
    assert error.rule is ValidationRule.INCLUDE_DENIED
    assert error.severity is Severity.ERROR
    assert '../secret.mjml' in str(exc_info.value)


def test_on_denied_accepts_the_string_value():
    assert IncludePolicy(on_denied='error').on_denied is IncludeDenied.ERROR
    with pytest.raises(ValueError):
        IncludePolicy(on_denied='explode')


def test_validate_reports_a_denial_and_never_raises(tree: Path):
    path = _template(tree, '<mj-include path="../secret.mjml" />')

    for on_denied, severity in [('warn', Severity.WARNING), ('error', Severity.ERROR)]:
        with path.open('rb') as mjml_fp:
            (error,) = validate(mjml_fp, includes=IncludePolicy(on_denied=on_denied))
        assert error.rule is ValidationRule.INCLUDE_DENIED
        assert error.severity is severity


@pytest.mark.parametrize('level', ['skip', 'soft', 'strict'])
def test_discarded_denials_remain_fatal_under_every_level(discarded_denial_templates, level: str):
    policy = IncludePolicy(on_denied=IncludeDenied.ERROR)

    for case, path, expected_file, expected_line, expected_include in discarded_denial_templates:
        with pytest.raises(IncludeAccessError) as exc_info:
            _render(path, policy, validation_level=level)

        assert len(exc_info.value.errors) == 1, case
        (error,) = exc_info.value.errors
        assert error.rule is ValidationRule.INCLUDE_DENIED
        assert error.file == str(expected_file)
        assert error.line == expected_line
        assert error.included_in == expected_include


def test_discarded_denials_are_reported_once_under_skip_and_validation(
    discarded_denial_templates,
):
    for case, path, expected_file, expected_line, expected_include in discarded_denial_templates:
        result = _render(path, validation_level='skip')
        with path.open('rb') as mjml_fp:
            validation_errors = validate(mjml_fp, includes=IncludePolicy())

        for errors in (result.errors, validation_errors):
            denials = [error for error in errors if error.rule is ValidationRule.INCLUDE_DENIED]
            assert len(denials) == 1, case
            (error,) = denials
            assert error.severity is Severity.WARNING
            assert error.file == str(expected_file)
            assert error.line == expected_line
            assert error.included_in == expected_include


def test_discarded_disabled_includes_are_reported_once_under_skip_and_validation(
    tmp_path: Path,
):
    path = tmp_path / 'template.mjml'
    path.write_text(
        '<mj-include path="before.mjml" />\n'
        '<mjml><mj-body>\n'
          '<mj-include path="outer.mjml">\n'
            '<mj-include path="inner.mjml" />\n'
          '</mj-include>\n'
        '</mj-body></mjml>'
    )

    result = _render(path, policy=None, validation_level='skip')
    with path.open('rb') as mjml_fp:
        validation_errors = validate(mjml_fp)

    for errors in (result.errors, validation_errors):
        assert [error.rule for error in errors] == [ValidationRule.INCLUDE_DISABLED] * 3
        assert {error.line for error in errors} == {1, 3, 4}


def test_directory_inside_the_root_is_an_include_error_not_a_denial(tree: Path):
    result = _render(_template(tree, '<mj-include path="sub" />'))

    (error,) = result.errors
    assert error.rule is ValidationRule.INCLUDE_ERROR
    assert 'not a regular file' in error.message
    assert 'mj-include fails to read file' in result.html


def test_fifo_inside_the_root_is_not_read(tree: Path):
    if not hasattr(os, 'mkfifo'):
        pytest.skip('this platform has no FIFOs')
    os.mkfifo(tree / 'pipe.mjml')
    path = _template(tree, '<mj-include path="pipe.mjml" />')
    script = (
        'import sys\n'
        'from mjml import IncludePolicy, validate\n'
        'with open(sys.argv[1], "rb") as mjml_fp:\n'
        '    errors = validate(mjml_fp, includes=IncludePolicy())\n'
        'print(*(error.rule.value for error in errors))\n'
    )

    # reading the FIFO would block forever, so the check runs with a deadline
    completed = subprocess.run(
        [sys.executable, '-c', script, str(path)],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )

    assert completed.stdout.split() == ['include-error']


def _template(templates: Path, include: str) -> Path:
    path = templates / 'template.mjml'
    path.write_text(f'<mjml><mj-body>{include}<mj-section /></mj-body></mjml>')
    return path


def _render(path: Path, policy: Optional[IncludePolicy] = IncludePolicy(), **kwargs):
    with path.open('rb') as mjml_fp:
        return mjml_to_html(mjml_fp, includes=policy, **kwargs)


def assert_denied(result, reason: str = '') -> None:
    assert DENIED in result.html
    assert 'SECRET' not in result.html
    (error,) = result.errors
    assert error.rule is ValidationRule.INCLUDE_DENIED
    assert error.severity is Severity.WARNING
    assert error.tag_name == 'mj-include'
    assert reason in error.message
