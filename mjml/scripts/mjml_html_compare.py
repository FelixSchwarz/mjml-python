import sys
from pathlib import Path

from htmlcompare import assert_same_html

from mjml import mjml_to_html


def main():
    mjml_filename = Path(sys.argv[1])
    html_filename = Path(sys.argv[2])

    with mjml_filename.open("rb") as mjml_fp:
        result = mjml_to_html(mjml_fp)

    with html_filename.open(encoding="utf8") as html_fp:
        expected_html = html_fp.read()

    assert not result.errors
    actual_html = result.html
    assert_same_html(expected_html, actual_html, verbose=True)
