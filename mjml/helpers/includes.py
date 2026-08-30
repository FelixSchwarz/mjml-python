from io import BytesIO
from pathlib import PurePath

from bs4 import BeautifulSoup


__all__ = ['parse_include_document', 'read_include_file', 'resolve_include_path']


def resolve_include_path(path_value, *, template_dir):
    path = PurePath(path_value)
    if path.is_absolute():
        return path
    elif template_dir:
        return template_dir / path
    return path


def read_include_file(path_value, *, template_dir) -> str:
    included_path = resolve_include_path(path_value, template_dir=template_dir)
    with open(included_path, 'rb') as fp:
        return fp.read().decode('utf8')


def parse_include_document(path_value, *, template_dir) -> BeautifulSoup:
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
    # lxml does not like non-ascii StringIO input but utf8-encoded BytesIO works
    # seen with pypy3 7.3.1, lxml 4.6.3 (Fedora 34)
    fp_included = BytesIO(included_bytes)
    return BeautifulSoup(fp_included, 'html.parser')
