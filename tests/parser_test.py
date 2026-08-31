from pathlib import Path
from typing import Optional

import pytest
from bs4 import BeautifulSoup

from mjml._node_adapter import node_tree_from_soup
from mjml.core.registry import core_components
from mjml.node import Node, NodeKind
from mjml.parser import parse_document


# "mj-include" is resolved by the adapter but not by the parser yet, so those
# templates cannot be compared until the parser resolves includes as well
CORPUS = {
    path.stem: path
    for directory in (Path(__file__).parent / 'testdata',
                      Path(__file__).parent / 'missing_functionality')
    for path in sorted(directory.glob('*.mjml'))
    if not path.stem.startswith('_') and 'mj-include' not in path.read_text(encoding='utf8')
}
CORPUS_IDS = sorted(CORPUS)


def test_can_build_tree_of_elements():
    root = _parse(_body('<mj-section><mj-column><mj-divider /></mj-column></mj-section>'))

    assert root.tag_name == 'mjml'
    assert [child.tag_name for child in root.children] == ['mj-body']
    section = _find(root, 'mj-section')
    assert [child.tag_name for child in section.children] == ['mj-column']


def test_returns_none_without_an_mjml_element():
    mjml_str = '<div>no mjml here</div>'
    root = parse_document(mjml_str, core_components(), file=None)

    assert root is None


def test_does_not_descend_into_ending_tags():
    mj_text = _find(_parse(_body('<mj-text>hello <b>world</b></mj-text>')), 'mj-text')

    assert mj_text.children == ()
    assert mj_text.content == 'hello <b>world</b>'


def test_copies_content_of_an_ending_tag_verbatim():
    # single quotes, attribute casing and entities all survive
    inner = '<mj-text>a &lt;script&gt; <B Class=\'x\'>c</B> &#233;</mj-text>'
    mj_text = _find(_parse(_body(inner)), 'mj-text')

    assert mj_text.content == "a &lt;script&gt; <B Class='x'>c</B> &#233;"


def test_a_self_closing_ending_tag_has_no_content():
    mj_text = _find(_parse(_body('<mj-text />')), 'mj-text')

    assert mj_text.content == ''
    assert mj_text.children == ()


def test_a_nested_tag_of_the_same_name_stays_inside_the_content():
    mj_text = _find(_parse(_body('<mj-text>a<mj-text>b</mj-text>c</mj-text>')), 'mj-text')

    assert mj_text.content == 'a<mj-text>b</mj-text>c'
    assert mj_text.children == ()


def test_keeps_casing_for_attribute_names():
    section = _find(_parse(_body('<mj-section Color="red" full-width="false" />')), 'mj-section')

    assert 'Color' in section.attributes
    assert section.attributes['Color'] == 'red'
    assert section.attributes['full-width'] is False


def test_comments_are_their_own_kind_and_carry_a_position():
    mj_body = _find(_parse('<mjml>\n<mj-body>\n<!-- note --><mj-section />\n</mj-body>\n</mjml>'),
                   'mj-body')

    comment, section = mj_body.children
    assert comment.kind is NodeKind.COMMENT
    assert comment.content == '<!-- note -->'
    assert (comment.line, comment.column) == (3, 0)
    assert section.kind is NodeKind.ELEMENT


def test_nodes_carry_the_source_position_and_file():
    source = '<mjml>\n  <mj-body>\n    <mj-section />\n  </mj-body>\n</mjml>'
    section = _find(_parse(source, file='/tmp/template.mjml'), 'mj-section')

    assert (section.line, section.column) == (3, 4)
    assert section.file == '/tmp/template.mjml'


def test_text_of_a_non_ending_tag_becomes_its_content():
    section = _find(_parse(_body('<mj-section>stray text</mj-section>')), 'mj-section')

    assert section.content == 'stray text'


def _shape(node):
    # attribute names are compared lower-cased: only the parser keeps the case
    # they were written in, which is the point of having it
    return (
        node.tag_name,
        node.kind,
        tuple(sorted((name.lower(), value) for name, value in node.attributes.items())),
        tuple(_shape(child) for child in node.children),
    )


@pytest.mark.parametrize('test_id', CORPUS_IDS)
def test_the_parser_and_the_adapter_agree(test_id):
    # the adapter is what the validator runs on today, so the parser has to
    # describe the same document before it can take over
    path = CORPUS[test_id]
    source = path.read_text(encoding='utf8')
    components = core_components()

    adapted = node_tree_from_soup(
        BeautifulSoup(source, 'html.parser').mjml, components, template_dir=path.parent
    )
    parsed = parse_document(source, components)

    assert _shape(parsed) == _shape(adapted)


def test_an_attribute_without_a_value_is_an_empty_string():
    mjml_str = '<mj-wrapper full-width><mj-section /></mj-wrapper>'
    wrapper = _find(_parse(_body(mjml_str)), 'mj-wrapper')

    assert wrapper.attributes['full-width'] == ''


@pytest.mark.parametrize('content', [
    'one</mj-text><b>two</b>',
    'one<mj-text>two</mj-text></mj-text><b>three</b>',
    'one<mj-text>two',
])
def test_unmatched_closing_tags_do_not_end_raw_content(content):
    raw = _find(_parse(_body(f'<mj-raw>{content}</mj-raw><mj-section />')), 'mj-raw')

    assert raw.content == content
    assert raw.children == ()


def _parse(source: str, file: Optional[str] = None) -> Node:
    root = parse_document(source, core_components(), file=file)
    assert root is not None
    return root


def _find(node: Node, tag_name: str) -> Node:
    if node.tag_name == tag_name:
        return node
    for child in node.children:
        match = _find(child, tag_name)
        if match is not None:
            return match
    raise AssertionError(f'no node found with tag name {tag_name}')


def _body(inner: str) -> str:
    return f'<mjml><mj-body>{inner}</mj-body></mjml>'
