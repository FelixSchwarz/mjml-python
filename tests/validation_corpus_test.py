from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from mjml._node_adapter import node_tree_from_soup
from mjml.core.registry import components_for_invocation
from mjml.elements import MjText
from mjml.validator import validate_tree


TESTDATA_DIR = Path(__file__).parent / 'testdata'
IMPORTED_DIR = Path(__file__).parent / 'missing_functionality'


class MjTextCustom(MjText):
    component_name = 'mj-text-custom'


def template_ids(directory):
    # files starting with "_" are include targets, not templates
    return sorted(path.stem for path in directory.glob('*.mjml') if not path.stem.startswith('_'))


def validation_errors(path, directory):
    components = components_for_invocation([MjTextCustom])
    soup = BeautifulSoup(path.read_bytes(), 'html.parser')
    assert soup.mjml is not None, f'{path} has no <mjml> element'
    tree = node_tree_from_soup(soup.mjml, components, file=str(path), template_dir=directory)
    return validate_tree(tree, components)


@pytest.mark.parametrize('test_id', template_ids(TESTDATA_DIR))
def test_every_template_we_render_validates(test_id):
    errors = validation_errors(TESTDATA_DIR / f'{test_id}.mjml', TESTDATA_DIR)

    assert len(errors) == 0


# mjml JS rejects this one as well: "mj-hero" has no "width" attribute.
UPSTREAM_REJECTS_TOO = {'mj-hero-width': ['Attribute width is illegal']}


@pytest.mark.parametrize('test_id', template_ids(IMPORTED_DIR))
def test_imported_templates_validate(test_id):
    # these render incorrectly for now, but they are valid mjml
    errors = validation_errors(IMPORTED_DIR / f'{test_id}.mjml', IMPORTED_DIR)

    assert [error.message for error in errors] == UPSTREAM_REJECTS_TOO.get(test_id, [])
