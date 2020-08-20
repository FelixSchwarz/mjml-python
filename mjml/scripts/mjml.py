#!/usr/bin/env python3
"""
mjml.

Usage:
  mjml <MJML-FILE>
  mjml <MJML-FILE> -o <OUTPUT-FILE>
"""

from io import BytesIO
from pathlib import Path
import sys

from docopt import docopt

from mjml.mjml2html import mjml_to_html


def main():
    arguments = docopt(__doc__)
    mjml_filename = arguments['<MJML-FILE>']
    output_filename = arguments['<OUTPUT-FILE>']

    if mjml_filename == '-':
        stdin = sys.stdin.buffer
        mjml_fp = BytesIO(stdin.read())
        result = mjml_to_html(mjml_fp)
    else:
        with Path(mjml_filename).open('rb') as mjml_fp:
            result = mjml_to_html(mjml_fp)
    assert not result.errors, result.errors

    html_str = result.html
    if output_filename:
        with Path(output_filename).open('w') as html_fp:
            html_fp.write(html_str)
    else:
        print(html_str)


if __name__ == '__main__':
    main()

