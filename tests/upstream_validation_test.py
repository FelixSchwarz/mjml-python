import json
import re
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from mjml._node_adapter import node_tree_from_soup
from mjml.core.registry import core_components
from mjml.errors import ValidationRule
from mjml.validator import validate_tree


TEMPLATE_DIR = Path(__file__).parent / 'validation_templates'
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


PARITY_TEMPLATES = sorted(
    test_id for test_id, upstream in UPSTREAM_FINDINGS.items()
    if upstream and not test_id.startswith('deviation-')
)


@pytest.mark.parametrize('test_id', PARITY_TEMPLATES)
def test_everything_upstream_rejects_is_rejected_here(test_id):
    upstream = {tuple(row) for row in UPSTREAM_FINDINGS[test_id]}

    missing = upstream - set(findings(test_id))
    assert not missing


def test_the_snapshot_covers_every_template():
    templates = {path.stem for path in TEMPLATE_DIR.glob('*.mjml')}
    assert templates == set(UPSTREAM_FINDINGS)


@pytest.mark.parametrize('test_id', PARITY_TEMPLATES)
def test_every_invalid_template_is_rejected(test_id):
    # a template nobody rejects does not belong in this corpus
    assert findings(test_id)


# The values these templates use are rejected here although mjml js accepts
# them: its matchers are unanchored or treat things like "1,2px" as a number.
# The empty upstream finding list in the snapshot is the record of that.
DEVIATIONS = {
    'deviation-integer-unanchored': ('mj-table', 'valid-types', 'cellpadding'),
    'deviation-rgb-unanchored': ('mj-text', 'valid-types', 'color'),
    'deviation-rgba-unanchored': ('mj-text', 'valid-types', 'color'),
    'deviation-unit-number': ('mj-text', 'valid-types', 'font-size'),
    'deviation-unit-with-negative-number': ('mj-text', 'valid-types', 'letter-spacing'),
}


def test_the_deviations_are_the_documented_ones():
    from_corpus = {test_id for test_id in UPSTREAM_FINDINGS if test_id.startswith('deviation-')}
    assert from_corpus == set(DEVIATIONS)


@pytest.mark.parametrize('test_id', sorted(DEVIATIONS))
def test_upstream_accepts_what_we_reject(test_id):
    assert UPSTREAM_FINDINGS[test_id] == []
    assert findings(test_id) == [DEVIATIONS[test_id]]


# A comment is a node of its own here, so the validator skips it. mjml js turns
# it into an "mj-raw" element, which four of these five parents accept anyway.
# "mj-carousel" does not, and mjml 5.4.0 crashes on it ("component.renderRadio
# is not a function") instead of reporting anything - as does this port.
COMMENT_PROBES = sorted(
    test_id for test_id in UPSTREAM_FINDINGS if test_id.startswith('comment-')
)


@pytest.mark.parametrize('test_id', COMMENT_PROBES)
def test_a_comment_is_never_an_illegal_child(test_id):
    assert findings(test_id) == []
    # nothing upstream reports for these either
    assert UPSTREAM_FINDINGS[test_id] in ([], None)


def test_the_comment_probes_cover_every_restrictive_parent():
    parents = {test_id[len('comment-in-'):] for test_id in COMMENT_PROBES}
    assert parents == {'mj-carousel', 'mj-group', 'mj-social', 'mj-navbar', 'mj-accordion'}
