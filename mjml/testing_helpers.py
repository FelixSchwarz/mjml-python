
from contextlib import contextmanager
from pathlib import Path
from typing import Union


__all__ = ['get_mjml_fp', 'load_expected_html']

TESTDATA_DIR = Path(__file__).parent / '..' / 'tests' / 'testdata'

def load_expected_html(test_id, suffix: Union[str, None] = None) -> str:
    html_filename = f'{test_id}-expected{suffix or ""}.html'
    html_path = TESTDATA_DIR / html_filename
    return html_path.read_text()

@contextmanager
def get_mjml_fp(test_id, json=False):
    mjml_filename = f'{test_id}.mjml'
    if json:
        mjml_filename += '.json'
    with (TESTDATA_DIR / mjml_filename).open('rb') as mjml_fp:
        yield mjml_fp
