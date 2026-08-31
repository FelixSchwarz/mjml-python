from pathlib import Path
from typing import Optional

import pytest

from mjml import Include, ValidationRule
from mjml.core.registry import core_components
from mjml.node import Node, NodeKind
from mjml.parser import parse_document


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


def test_an_included_body_is_spliced_in_with_its_provenance(tmp_path: Path):
    path = _include_template(
        tmp_path, '<mj-include path="./part.mjml" />',
        part='<mj-section><mj-column /></mj-section>',
    )
    mj_body = _find(_parse_file(path), 'mj-body')

    (section,) = mj_body.children
    assert section.tag_name == 'mj-section'
    assert section.file == str(tmp_path / 'part.mjml')
    assert section.included_in == (Include(file=str(path), line=1),)


def test_reports_unreadable_include(tmp_path: Path):
    path = _include_template(tmp_path, '<mj-include path="./missing.mjml" />')
    (raw,) = _find(_parse_file(path), 'mj-body').children

    (error,) = raw.errors
    assert error.rule is ValidationRule.INCLUDE_ERROR
    assert 'could not read the included file' in error.message


def test_reports_circular_include(tmp_path: Path):
    path = _include_template(
        tmp_path, '<mj-include path="./part.mjml" />',
        part='<mj-include path="./part.mjml" />',
    )
    (raw,) = _find(_parse_file(path), 'mj-body').children

    (error,) = raw.errors
    assert 'Circular inclusion' in error.message

def test_head_of_an_included_file_joins_the_document_head(tmp_path: Path):
    mjml_str = (
        '<mjml>'
        '<mj-head><mj-preview>p</mj-preview></mj-head>'
        '<mj-body><mj-include path="./part.mjml" /></mj-body>'
        '</mjml>'
    )
    path = tmp_path / 'template.mjml'
    path.write_text(mjml_str)
    included_mjml = (
        '<mjml>'
        '<mj-head><mj-title>from the include</mj-title></mj-head>'
        '<mj-body><mj-section><mj-column /></mj-section></mj-body>'
        '</mjml>'
    )
    (tmp_path / 'part.mjml').write_text(included_mjml)

    head = _find(_parse_file(path), 'mj-head')

    assert [child.tag_name for child in head.children] == ['mj-preview', 'mj-title']


def test_only_the_first_head_and_body_of_an_included_file_are_used(tmp_path: Path):
    # js: findTag() stops at the first match
    (tmp_path / 'part.mjml').write_text(
        '<mjml>'
        '<mj-head><mj-title>first</mj-title></mj-head>'
        '<mj-head><mj-title>second</mj-title></mj-head>'
        '<mj-body><mj-section css-class="first" /></mj-body>'
        '<mj-body><mj-section css-class="second" /></mj-body>'
        '</mjml>'
    )
    path = tmp_path / 'template.mjml'
    path.write_text('<mjml><mj-body><mj-include path="./part.mjml" /></mj-body></mjml>')
    tree = _parse_file(path)

    (title,) = _find(tree, 'mj-head').children
    assert title.content == 'first'
    (section,) = _find(tree, 'mj-body').children
    assert section.attributes['css-class'] == 'first'


def test_a_document_without_a_head_gets_one_from_the_include(tmp_path: Path):
    (tmp_path / 'part.mjml').write_text(
        '<mjml><mj-head><mj-title>from the include</mj-title></mj-head>'
        '<mj-body><mj-section><mj-column /></mj-section></mj-body></mjml>'
    )
    path = tmp_path / 'template.mjml'
    path.write_text('<mjml><mj-body><mj-include path="./part.mjml" /></mj-body></mjml>')

    head = _find(_parse_file(path), 'mj-head')

    assert [child.tag_name for child in head.children] == ['mj-title']


def test_html_include_is_not_parsed_as_mjml(tmp_path: Path):
    path = tmp_path / 'template.mjml'
    mjml_str = '<mjml><mj-body><mj-include path="./part.html" type="html" /></mj-body></mjml>'
    path.write_text(mjml_str)
    (tmp_path / 'part.html').write_text('<div class="raw">not mjml</div>')

    (raw,) = _find(_parse_file(path), 'mj-body').children

    assert raw.tag_name == 'mj-raw'
    assert raw.content == '<div class="raw">not mjml</div>'


def test_css_include_becomes_a_style_element_in_the_head(tmp_path: Path):
    path = tmp_path / 'template.mjml'
    mjml_str = (
        '<mjml>'
        '<mj-body>'
          '<mj-include path="./part.css" type="css" css-inline="inline" />'
          '<mj-section><mj-column /></mj-section>'
        '</mj-body>'
        '</mjml>'
    )
    path.write_text(mjml_str)
    (tmp_path / 'part.css').write_text('.red { color: red; }')

    head = _find(_parse_file(path), 'mj-head')

    (style,) = head.children
    assert style.tag_name == 'mj-style'
    assert style.content == '.red { color: red; }'
    # "css-inline" decides whether the rules are inlined into the elements
    assert style.attributes == {'inline': 'inline'}


@pytest.mark.parametrize('is_nested', [False, True])
def test_css_includes_follow_the_heads_of_included_templates(tmp_path: Path, is_nested: bool):
    mjml_str = (
        '<mjml>'
        '<mj-head><mj-include path="last.css" type="css" /></mj-head>'
        '<mj-body><mj-include path="part.mjml" /></mj-body>'
        '</mjml>'
    )
    (tmp_path / 'last.css').write_text('.x { color: red; }')
    included_part_mjml = (
        '<mjml>'
          '<mj-head><mj-style>.x { color: blue; }</mj-style></mj-head>'
          '<mj-body><mj-section /></mj-body>'
        '</mjml>'
    )
    (tmp_path / 'part.mjml').write_text(included_part_mjml)
    if is_nested:
        (tmp_path / 'nested.mjml').write_text(mjml_str)
        mjml_str = '<mjml><mj-body><mj-include path="nested.mjml" /></mj-body></mjml>'
    path = tmp_path / 'template.mjml'
    path.write_text(mjml_str)

    head = _find(_parse_file(path), 'mj-head')

    actual_css = [child.content for child in head.children]
    assert actual_css == ['.x { color: blue; }', '.x { color: red; }']


def _parse(source: str, file: Optional[str] = None) -> Node:
    root = parse_document(source, core_components(), file=file)
    assert root is not None
    return root


def _parse_file(path: Path, **kwargs) -> Node:
    mjml_str = path.read_text(encoding='utf8')
    # The tests below look at reported problems, so parsing must not raise.
    root = parse_document(
        mjml_str, core_components(), file=str(path), template_dir=path.parent,
        report_include_errors=True, **kwargs
    )
    assert root is not None
    return root


def _find(node: Node, tag_name: str) -> Node:
    def search(current: Node) -> Optional[Node]:
        if current.tag_name == tag_name:
            return current
        for child in current.children:
            match = search(child)
            if match is not None:
                return match
        return None

    match = search(node)
    if match is None:
        raise AssertionError(f'no node found with tag name {tag_name}')
    return match


def _body(inner: str) -> str:
    return f'<mjml><mj-body>{inner}</mj-body></mjml>'


def _include_template(tmp_path: Path, include: str, **parts: str) -> Path:
    for name, content in parts.items():
        (tmp_path / f'{name}.mjml').write_text(content)
    path = tmp_path / 'template.mjml'
    path.write_text(f'<mjml><mj-body>{include}</mj-body></mjml>')
    return path
