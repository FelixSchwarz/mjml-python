
from contextlib import contextmanager
from pathlib import Path


__all__ = ['get_mjml_fp', 'load_expected_html']

TESTDATA_DIR = Path(__file__).parent / '..' / 'tests' / 'testdata'

def load_expected_html(test_id):
    html_filename = f'{test_id}-expected.html'
    with (TESTDATA_DIR / html_filename).open('rb') as html_fp:
        expected_html = html_fp.read()
    return expected_html

@contextmanager
def get_mjml_fp(test_id, json=False):
    mjml_filename = f'{test_id}.mjml'
    if json:
        mjml_filename += '.json'
    with (TESTDATA_DIR / mjml_filename).open('rb') as mjml_fp:
        yield mjml_fp
