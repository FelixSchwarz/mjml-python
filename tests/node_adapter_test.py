from bs4 import BeautifulSoup

from mjml._node_adapter import node_tree_from_soup
from mjml.core.registry import register_core_components
from mjml.node import NodeKind


def build_tree(mjml_str, file=None):
    components = register_core_components()
    soup = BeautifulSoup(mjml_str, 'html.parser')
    return node_tree_from_soup(soup.mjml, components, file=file)


def find_node(node, tag_name):
    if node.tag_name == tag_name:
        return node
    for child in node.children:
        match = find_node(child, tag_name)
        if match is not None:
            return match
    return None


def test_builds_a_tree_of_elements():
    mjml_str = (
        '<mjml><mj-body>'
        '<mj-section><mj-column><mj-divider /></mj-column></mj-section>'
        '</mj-body></mjml>'
    )
    root = build_tree(mjml_str)

    assert root.tag_name == 'mjml'
    assert [child.tag_name for child in root.children] == ['mj-body']
    section = find_node(root, 'mj-section')
    assert [child.tag_name for child in section.children] == ['mj-column']


def test_does_not_descend_into_ending_tags():
    mjml_str = '<mjml><mj-body><mj-text>hello <b>world</b></mj-text></mj-body></mjml>'
    mj_text = find_node(build_tree(mjml_str), 'mj-text')

    assert mj_text.children == ()
    assert mj_text.content == 'hello <b>world</b>'


def test_escaped_content_of_an_ending_tag_stays_escaped():
    mjml_str = '<mjml><mj-body><mj-text>&lt;script&gt;</mj-text></mj-body></mjml>'
    mj_text = find_node(build_tree(mjml_str), 'mj-text')

    assert mj_text.content == '&lt;script&gt;'


def test_comments_are_their_own_kind():
    mjml_str = '<mjml><mj-body><!-- note --><mj-section /></mj-body></mjml>'
    mj_body = find_node(build_tree(mjml_str), 'mj-body')

    comment, section = mj_body.children
    assert comment.kind is NodeKind.COMMENT
    assert comment.content == '<!-- note -->'
    assert section.kind is NodeKind.ELEMENT


def test_converts_boolean_attribute_values():
    mjml_str = '<mjml><mj-body><mj-section full-width="false" /></mj-body></mjml>'
    section = find_node(build_tree(mjml_str), 'mj-section')

    assert section.attributes['full-width'] is False


def test_nodes_carry_the_source_position_and_file():
    mjml_str = '<mjml>\n  <mj-body>\n    <mj-section />\n  </mj-body>\n</mjml>'
    section = find_node(build_tree(mjml_str, file='/tmp/template.mjml'), 'mj-section')

    assert section.line == 3
    assert section.column == 4
    assert section.file == '/tmp/template.mjml'


def test_adapter_cannot_tell_apart_attributes_which_differ_only_in_case():
    # BeautifulSoup lower-cases attribute names while mjml keeps them as
    # written, so "Color" cannot be reported as an unknown attribute. The
    # parser stage has to close this gap.
    mjml_str = '<mjml><mj-body><mj-section Color="red" /></mj-body></mjml>'
    section = find_node(build_tree(mjml_str), 'mj-section')

    assert 'Color' not in section.attributes
    assert section.attributes['color'] == 'red'
