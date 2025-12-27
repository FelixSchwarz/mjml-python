#!/usr/bin/env python3
"""
mjml.

Usage:
  mjml [options] <MJML-FILE>
  mjml [options] <MJML-FILE> -o <OUTPUT-FILE>

Options:
  --template-dir=<path>    base dir for mj-include (default: path of mjml file)
  --config.keepComments=False  whether comments in mjml should be present in the generated html (default: true)
"""
# ruff: noqa: E501

import sys
from io import BytesIO
from pathlib import Path
from typing import Union

from docopt import docopt

from mjml.mjml2html import mjml_to_html


def main():
    arguments = docopt(__doc__)
    mjml_filename = arguments['<MJML-FILE>']
    output_filename = arguments['<OUTPUT-FILE>']
    template_dir = arguments['--template-dir']
    keep_comments_str = arguments['--config.keepComments']
    keep_comments = _parse_bool(keep_comments_str, default=True)
    if keep_comments is None:
        sys.stderr.write("value for --config.keepComments should be either true or false\n")
        sys.exit(1)

    if mjml_filename == '-':
        stdin = sys.stdin.buffer
        mjml_fp = BytesIO(stdin.read())
        result = mjml_to_html(mjml_fp, template_dir=template_dir, keep_comments=keep_comments)
    else:
        with Path(mjml_filename).open('rb') as mjml_fp:
            result = mjml_to_html(mjml_fp, template_dir=template_dir, keep_comments=keep_comments)
    assert not result.errors, result.errors

    html_str = result.html
    if output_filename:
        with Path(output_filename).open('w') as html_fp:
            html_fp.write(html_str)
    else:
        # always return "binary" data (HTML encoded as UTF-8 to avoid encoding
        # problems in Windows:
        #   UnicodeEncodeError: 'charmap' codec can't encode character '\ufb02' in position …: character maps to <undefined>
        html_bytes = html_str.encode('utf8')
        sys.stdout.buffer.write(html_bytes)


def _parse_bool(value: Union[str, None], *, default: bool) -> Union[bool, None]:
    if value is None:
        return default
    truthy = {'true', '1', 'yes', 'y'}
    falsey = {'false', '0', 'no', 'n'}

    value_lower = value.strip().lower()
    if value_lower in truthy:
        return True
    elif value_lower in falsey:
        return False
    else:
        return None


if __name__ == '__main__':
    main()
