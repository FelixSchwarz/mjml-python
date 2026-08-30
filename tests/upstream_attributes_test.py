import json
from pathlib import Path

from mjml.core.registry import core_components


_snapshot = json.loads(
    (Path(__file__).parent / 'upstream_attributes.json').read_text(encoding='utf8')
)
UPSTREAM_ATTRS = _snapshot['allowed_attributes']
UPSTREAM_ENDING_TAGS = set(_snapshot['ending_tags'])

_CSS_CLASS_IS_GLOBAL = (
    'upstream whitelists "css-class" in its validator instead of declaring it '
    'per component, we have to declare it so "get_attr()" does not raise'
)
ACCEPTED_DELTA = {
    ('missing', 'mj-raw', 'position'): 'position="file-start" is not implemented (#74)',
    **{
        ('extra', component_name, 'css-class'): _CSS_CLASS_IS_GLOBAL
        for component_name in (
            'mj-body', 'mj-button', 'mj-column', 'mj-divider',
            'mj-image', 'mj-table', 'mj-text',
        )
    },
}


def divergences_from_upstream():
    delta = {}
    components = core_components()
    for component_name in sorted(set(components) & set(UPSTREAM_ATTRS)):
        port = dict(components[component_name].allowed_attrs())
        upstream = UPSTREAM_ATTRS[component_name]
        for attr in sorted(set(upstream) - set(port)):
            delta[('missing', component_name, attr)] = upstream[attr]
        for attr in sorted(set(port) - set(upstream)):
            delta[('extra', component_name, attr)] = port[attr]
        for attr in sorted(set(port) & set(upstream)):
            if port[attr] != upstream[attr]:
                delta[('type', component_name, attr)] = f'{port[attr]} != {upstream[attr]}'
    return delta


def test_the_same_components_exist_upstream():
    assert set(core_components()) == set(UPSTREAM_ATTRS)


def test_the_same_components_are_ending_tags():
    ending_tags = {
        component_name
        for component_name, component_cls in core_components().items()
        if component_cls.ending_tag
    }
    assert ending_tags == UPSTREAM_ENDING_TAGS


def test_every_divergence_from_upstream_is_accepted():
    # a new divergence needs a decision, not an entry in "ACCEPTED_DELTA"
    unexpected = sorted(
        f'{kind} {component_name} {attr} ({value})'
        for (kind, component_name, attr), value in divergences_from_upstream().items()
        if (kind, component_name, attr) not in ACCEPTED_DELTA
    )
    assert not unexpected


def test_accepted_delta_lists_no_resolved_divergences():
    delta = divergences_from_upstream()
    resolved = sorted(' '.join(row) for row in ACCEPTED_DELTA if row not in delta)
    assert not resolved
