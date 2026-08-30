import json
import re
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from mjml._node_adapter import node_tree_from_soup
from mjml.core.registry import core_components
from mjml.errors import ValidationRule
from mjml.validator import validate_tree


TEMPLATE_DIR = Path(__file__).parent / 'invalid_templates'
UPSTREAM_FINDINGS = json.loads(
    (Path(__file__).parent / 'upstream_validation.json').read_text(encoding='utf8')
)

_ILLEGAL_ATTRS_RE = re.compile(r'^Attributes? ([\w, -]+?) (?:is|are) illegal$')
_INVALID_VALUE_RE = re.compile(r'^Attribute ([\w-]+) has invalid value:')


def findings(test_id):
    """The findings of this port as (element, rule, attribute) rows."""
    components = core_components()
    template = TEMPLATE_DIR / f'{test_id}.mjml'
    soup = BeautifulSoup(template.read_bytes(), 'html.parser')
    tree = node_tree_from_soup(soup.mjml, components, file=str(template))

    rows = []
    for error in validate_tree(tree, components):
        for attribute in _attributes(error):
            rows.append((error.tag_name, error.rule.value, attribute))
    return sorted(rows)


def _attributes(error):
    for rule, pattern in ((ValidationRule.VALID_ATTRIBUTES, _ILLEGAL_ATTRS_RE),
                          (ValidationRule.VALID_TYPES, _INVALID_VALUE_RE)):
        if error.rule is not rule:
            continue
        match = pattern.match(error.message)
        assert match is not None, f'cannot read the attributes from {error.message!r}'
        return match.group(1).split(', ')
    return [None]


@pytest.mark.parametrize('test_id', sorted(UPSTREAM_FINDINGS))
def test_everything_upstream_rejects_is_rejected_here(test_id):
    upstream = {tuple(row) for row in UPSTREAM_FINDINGS[test_id]}

    missing = upstream - set(findings(test_id))
    assert not missing


def test_the_snapshot_covers_every_template():
    templates = {path.stem for path in TEMPLATE_DIR.glob('*.mjml')}
    assert templates == set(UPSTREAM_FINDINGS)


@pytest.mark.parametrize('test_id', sorted(UPSTREAM_FINDINGS))
def test_every_invalid_template_is_rejected(test_id):
    # a template nobody rejects does not belong in this corpus
    assert findings(test_id)
