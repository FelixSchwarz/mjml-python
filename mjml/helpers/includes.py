from collections.abc import Sequence
from pathlib import Path, PurePath
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from _typeshed import StrPath


__all__ = [
    'CircularIncludeError',
    'guard_against_circular_include',
    'include_source',
    'read_include_file',
    'resolve_include_path',
]


class CircularIncludeError(Exception):
    pass


def guard_against_circular_include(
    included_path: "StrPath",
    include_chain: Sequence[Path],
) -> Sequence[Path]:
    """
    Return the include chain extended by "included_path".

    A file which includes itself, directly or through other files, would
    otherwise be expanded until the recursion limit stops it.
    """
    resolved = Path(included_path).resolve()
    if resolved in include_chain:
        raise CircularIncludeError(f'Circular inclusion detected on file : {resolved}')
    return (*include_chain, resolved)


def resolve_include_path(path_value: "StrPath", *, template_dir: Optional["StrPath"]) -> PurePath:
    path = PurePath(path_value)
    if path.is_absolute():
        return path
    elif template_dir:
        return PurePath(template_dir) / path
    return path


def read_include_file(path_value, *, template_dir) -> str:
    included_path = resolve_include_path(path_value, template_dir=template_dir)
    with open(included_path, 'rb') as fp:
        return fp.read().decode('utf8')


def include_source(path_value, *, template_dir) -> str:
    """The contents of an included file, wrapped in <mjml> if it has none."""
    return _included_bytes(path_value, template_dir=template_dir).decode('utf8')


def _included_bytes(path_value, *, template_dir) -> bytes:
    included_path = resolve_include_path(path_value, template_dir=template_dir)
    # Upstream mjml does not raise an error if the included file was not found.
    # Instead they generate a HTML comment with a failure notice.
    # using plain "open()" call because "PurePath" does not support ".open()"
    with open(included_path, 'rb') as fp:
        included_bytes = fp.read()
    # Need to load the included file as binary - otherwise non-ascii characters
    # in utf8-encoded include files were messed up on Windows.
    # Not sure what happens if lxml needs to handle non-utf8 contents but it
    # works for me at least for utf8 now.
    if b'<mjml>' not in included_bytes:
        included_bytes = b'<mjml><mj-body>' + included_bytes + b'</mj-body></mjml>'
    return included_bytes
