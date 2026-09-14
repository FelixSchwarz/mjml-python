import os
import re
import stat
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import TYPE_CHECKING, Union


if TYPE_CHECKING:
    from _typeshed import StrPath


__all__ = [
    'CircularIncludeError',
    'IncludeAccess',
    'IncludeDenial',
    'IncludePolicy',
    'guard_against_circular_include',
    'include_access',
    'include_source',
    'is_regular_file',
    'read_include_file',
    'resolve_include',
]


class CircularIncludeError(Exception):
    pass


@dataclass(frozen=True)
class IncludePolicy:
    """
    Enables "mj-include", which is off by default, and says what it may read.

    A template which may pull in files is only safe when every template is
    trusted, so mjml js requires the same opt-in since version 5. An enabled
    include may read files below "roots"; everything else is denied. Unlike in
    mjml js, the template directory is not allowed implicitly: the directories
    a template may read should not depend on how the template was passed in.
    """
    roots: Sequence["StrPath"]

    def __post_init__(self) -> None:
        roots = self.roots
        if isinstance(roots, (str, os.PathLike)):
            # one directory, not a sequence of its characters
            roots = (roots,)
        roots = tuple(roots)
        if not roots:
            raise ValueError('an include policy needs at least one root directory')
        object.__setattr__(self, 'roots', roots)


@dataclass(frozen=True)
class IncludeAccess:
    """An IncludePolicy with its directories resolved, fixed for a whole parse."""
    roots: tuple[Path, ...]


def include_access(policy: IncludePolicy) -> IncludeAccess:
    """
    Canonicalize the allowed directories once, before anything is read.

    A root which does not exist is a misconfiguration which must not pass
    silently.
    """
    roots = []
    for root in policy.roots:
        try:
            resolved = Path(root).resolve(strict=True)
        except (OSError, RuntimeError):
            raise ValueError(f'the include root "{root}" does not exist') from None
        if not resolved.is_dir():
            raise ValueError(f'the include root "{root}" is not a directory')
        roots.append(resolved)
    return IncludeAccess(roots=tuple(roots))


@dataclass(frozen=True)
class IncludeDenial:
    reason: str


_DRIVE_LETTER_RE = re.compile(r'^[a-zA-Z]:')


def _is_rooted(path: str) -> bool:
    # "C:..." and "\\..." are absolute on Windows only, but a template must not
    # be able to name a drive or a share on any platform. A leading "/" is not
    # absolute for Windows either, yet it replaces the whole path below the drive.
    return (
        PurePath(path).is_absolute()
        or (_DRIVE_LETTER_RE.match(path) is not None)
        or path.startswith(('/', '\\'))
    )


def resolve_include(
    path_value: str,
    *,
    template_dir: "StrPath",
    access: IncludeAccess,
) -> Union[Path, IncludeDenial]:
    """
    The canonical file an include names, or why it may not be read.

    Nothing is opened here. The returned path is the one the caller opens, so
    the file which was checked is the file which is read.
    """
    if '\0' in path_value:
        return IncludeDenial('the path contains a NUL byte')
    if _is_rooted(path_value):
        return IncludeDenial('the path is absolute')
    # A missing target and an existing one outside the roots get the same
    # message, and the canonical target is not named: a template author who
    # could tell the two apart, or read where a symlink points, could probe
    # the file system outside of the directories the template may read.
    allowed = ', '.join(f'"{root}"' for root in access.roots)
    denial = IncludeDenial(
        f'the path does not lead to a file below the allowed directories {allowed}'
    )
    try:
        target = (Path(template_dir) / path_value).resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        # a missing file, a symlink loop or a name the file system refuses:
        # mjml js denies everything realpathSync() cannot resolve
        return denial
    if not any(root in target.parents for root in access.roots):
        return denial
    return target


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


def is_regular_file(path: Path) -> bool:
    """
    Whether "path" may be opened for reading.

    A directory cannot be read, and opening a FIFO or a device file blocks
    until something else writes to it, so a template could stall the process.
    """
    try:
        return stat.S_ISREG(os.stat(path).st_mode)
    except OSError:
        return False


def read_include_file(included_path: Path) -> str:
    return included_path.read_bytes().decode('utf8')


def include_source(included_path: Path) -> str:
    """The contents of an included file, wrapped in <mjml> if it has none."""
    # Read as bytes so the encoding does not depend on the platform.
    included_bytes = included_path.read_bytes()
    if b'<mjml>' not in included_bytes:
        included_bytes = b'<mjml><mj-body>' + included_bytes + b'</mj-body></mjml>'
    return included_bytes.decode('utf8')
