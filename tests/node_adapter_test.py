from pathlib import Path

from bs4 import BeautifulSoup

from mjml import Include, ValidationRule
from mjml._node_adapter import node_tree_from_soup
from mjml.core.registry import core_components
from mjml.node import NodeKind


def test_builds_a_tree_of_elements():
    mjml_str = (
        '<mjml><mj-body>'
        '<mj-section><mj-column><mj-divider /></mj-column></mj-section>'
        '</mj-body></mjml>'
    )
    root = _build_tree(mjml_str)

    assert root.tag_name == 'mjml'
    assert [child.tag_name for child in root.children] == ['mj-body']
    section = _find_node(root, 'mj-section')
    assert [child.tag_name for child in section.children] == ['mj-column']


def test_does_not_descend_into_ending_tags():
    mjml_str = '<mjml><mj-body><mj-text>hello <b>world</b></mj-text></mj-body></mjml>'
    mj_text = _find_node(_build_tree(mjml_str), 'mj-text')

    assert mj_text.children == ()
    assert mj_text.content == 'hello <b>world</b>'


def test_escaped_content_of_an_ending_tag_stays_escaped():
    mjml_str = '<mjml><mj-body><mj-text>&lt;script&gt;</mj-text></mj-body></mjml>'
    mj_text = _find_node(_build_tree(mjml_str), 'mj-text')

    assert mj_text.content == '&lt;script&gt;'


def test_comments_are_their_own_kind():
    mjml_str = '<mjml><mj-body><!-- note --><mj-section /></mj-body></mjml>'
    mj_body = _find_node(_build_tree(mjml_str), 'mj-body')

    comment, section = mj_body.children
    assert comment.kind is NodeKind.COMMENT
    assert comment.content == '<!-- note -->'
    assert section.kind is NodeKind.ELEMENT


def test_converts_boolean_attribute_values():
    mjml_str = '<mjml><mj-body><mj-section full-width="false" /></mj-body></mjml>'
    section = _find_node(_build_tree(mjml_str), 'mj-section')

    assert section.attributes['full-width'] is False


def test_nodes_carry_the_source_position_and_file():
    mjml_str = '<mjml>\n  <mj-body>\n    <mj-section />\n  </mj-body>\n</mjml>'
    section = _find_node(_build_tree(mjml_str, file='/tmp/template.mjml'), 'mj-section')

    assert section.line == 3
    assert section.column == 4
    assert section.file == '/tmp/template.mjml'


def test_adapter_cannot_tell_apart_attributes_which_differ_only_in_case():
    # BeautifulSoup lower-cases attribute names while mjml keeps them as
    # written, so "Color" cannot be reported as an unknown attribute. The
    # parser stage has to close this gap.
    mjml_str = '<mjml><mj-body><mj-section Color="red" /></mj-body></mjml>'
    section = _find_node(_build_tree(mjml_str), 'mj-section')

    assert 'Color' not in section.attributes
    assert section.attributes['color'] == 'red'


def test_unreadable_include_becomes_a_raw_node_carrying_the_error(tmp_path: Path):
    mjml_str = '<mjml><mj-body><mj-include path="./missing.mjml" /></mj-body></mjml>'
    mj_body = _find_node(_build_tree(mjml_str, template_dir=tmp_path), 'mj-body')

    (raw,) = mj_body.children
    assert raw.tag_name == 'mj-raw'
    missing_path = tmp_path / 'missing.mjml'
    # upstream renders this comment in place of the include
    expected_comment = f'<!-- mj-include fails to read file : ./missing.mjml at {missing_path} -->'
    assert raw.content == expected_comment
    (error,) = raw.errors
    assert error.rule is ValidationRule.INCLUDE_ERROR
    assert error.message == f'could not read the included file "./missing.mjml" ({missing_path})'


def test_included_body_is_spliced_into_the_tree(tmp_path: Path):
    (tmp_path / 'header.mjml').write_text('<mj-section><mj-column /></mj-section>')
    mjml_str = '<mjml><mj-body><mj-include path="./header.mjml" /></mj-body></mjml>'
    mj_body = _find_node(_build_tree(mjml_str, template_dir=tmp_path), 'mj-body')

    assert [child.tag_name for child in mj_body.children] == ['mj-section']
    section = mj_body.children[0]
    assert section.file == str(tmp_path / 'header.mjml')
    assert section.included_in == (Include(file=None, line=1),)


def test_nested_includes_build_a_provenance_chain(tmp_path: Path):
    (tmp_path / 'outer.mjml').write_text('<mj-include path="./inner.mjml" />')
    (tmp_path / 'inner.mjml').write_text('<mj-include path="./missing.mjml" />')
    mjml_str = '<mjml><mj-body><mj-include path="./outer.mjml" /></mj-body></mjml>'
    root = _build_tree(mjml_str, file='/tmp/template.mjml', template_dir=tmp_path)

    (error,) = _find_node(root, 'mj-raw').errors
    assert error.included_in == (
        Include(file='/tmp/template.mjml', line=1),
        Include(file=str(tmp_path / 'outer.mjml'), line=1),
    )
    formatted = error.formatted_message()
    assert ', included at line 1 of file ' in formatted
    assert ', itself included at line 1 of file /tmp/template.mjml (mj-raw) - ' in formatted


def _build_tree(mjml_str, file=None, template_dir=None):
    components = core_components()
    soup = BeautifulSoup(mjml_str, 'html.parser')
    return node_tree_from_soup(soup.mjml, components, file=file, template_dir=template_dir)


def _find_node(node, tag_name):
    if node.tag_name == tag_name:
        return node
    for child in node.children:
        match = _find_node(child, tag_name)
        if match is not None:
            return match
    return None


def test_include_without_a_path_is_reported():
    mjml_str = '<mjml><mj-body><mj-include /></mj-body></mjml>'
    mj_body = _find_node(_build_tree(mjml_str), 'mj-body')

    (raw,) = mj_body.children
    (error,) = raw.errors
    assert error.rule is ValidationRule.INCLUDE_ERROR
    assert error.message == 'mj-include has no "path" attribute'


def test_include_of_a_file_without_mjml_is_reported(tmp_path: Path):
    # the "<mjml>" stops the file from being wrapped, but it is only a comment
    # so no <mjml> element remains
    (tmp_path / 'broken.mjml').write_text('<!-- <mjml> -->')
    mjml_str = '<mjml><mj-body><mj-include path="./broken.mjml" /></mj-body></mjml>'
    mj_body = _find_node(_build_tree(mjml_str, template_dir=tmp_path), 'mj-body')

    (raw,) = mj_body.children
    (error,) = raw.errors
    assert error.rule is ValidationRule.INCLUDE_ERROR
    assert 'contains no mjml' in error.message
