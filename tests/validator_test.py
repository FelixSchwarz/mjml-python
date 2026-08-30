from bs4 import BeautifulSoup

from mjml import ValidationRule
from mjml._node_adapter import node_tree_from_soup
from mjml.core.registry import core_components
from mjml.validator import validate_tree


def _validate(mjml_str, template_dir=None):
    components = core_components()
    soup = BeautifulSoup(mjml_str, 'html.parser')
    tree = node_tree_from_soup(soup.mjml, components, template_dir=template_dir)
    return validate_tree(tree, components)


def _body(inner):
    return f'<mjml><mj-body>{inner}</mj-body></mjml>'


def _column(inner):
    return _body(f'<mj-section><mj-column>{inner}</mj-column></mj-section>')


def test_a_valid_document_produces_no_errors():
    assert _validate(_column('<mj-text color="red">hello</mj-text>')) == []


def test_unknown_element_is_reported():
    (error,) = _validate(_column('<mj-nonexistent />'))

    assert error.rule is ValidationRule.VALID_TAG
    assert error.message == "Element mj-nonexistent doesn't exist or is not registered"
    assert error.tag_name == 'mj-nonexistent'


def test_tags_without_a_component_are_valid():
    mjml_str = (
        '<mjml><mj-head><mj-attributes>'
        '<mj-all font-family="Arial" /><mj-class name="blue" color="blue" />'
        '</mj-attributes></mj-head>'
        '<mj-body><mj-section><mj-column /></mj-section></mj-body></mjml>'
    )
    assert _validate(mjml_str) == []


def test_unknown_attribute_is_reported():
    (error,) = _validate(_column('<mj-text nonexistent="1">hi</mj-text>'))

    assert error.rule is ValidationRule.VALID_ATTRIBUTES
    assert error.message == 'Attribute nonexistent is illegal'


def test_several_unknown_attributes_are_reported_in_one_error():
    (error,) = _validate(_column('<mj-text foo="1" bar="2">hi</mj-text>'))

    assert error.message == 'Attributes foo, bar are illegal'


def test_global_attributes_are_always_allowed():
    inner = '<mj-section css-class="c" mj-class="m"><mj-column /></mj-section>'
    assert _validate(_body(inner)) == []


def test_attribute_with_an_invalid_value_is_reported():
    (error,) = _validate(_column('<mj-text color="not-a-color">hi</mj-text>'))

    assert error.rule is ValidationRule.VALID_TYPES
    assert error.message == 'Attribute color has invalid value: not-a-color for type Color'


def test_misplaced_child_is_reported_with_its_possible_parents():
    (error,) = _validate(_body('<mj-section><mj-text>hi</mj-text></mj-section>'))

    assert error.rule is ValidationRule.VALID_CHILDREN
    expected = 'mj-text cannot be used inside mj-section, only inside: mj-column, mj-hero'
    assert error.message == expected
    # the error points at the child, not at the parent
    assert error.tag_name == 'mj-text'


def test_mj_attributes_accepts_any_element():
    mjml_str = (
        '<mjml><mj-head><mj-attributes>'
        '<mj-text color="red" /><mj-button font-size="12px" />'
        '</mj-attributes></mj-head>'
        '<mj-body><mj-section><mj-column /></mj-section></mj-body></mjml>'
    )
    assert _validate(mjml_str) == []


def test_attributes_inside_mj_attributes_are_still_validated():
    mjml_str = (
        '<mjml><mj-head><mj-attributes><mj-text color="bogus" /></mj-attributes></mj-head>'
        '<mj-body><mj-section><mj-column /></mj-section></mj-body></mjml>'
    )
    (error,) = _validate(mjml_str)

    assert error.rule is ValidationRule.VALID_TYPES


def test_children_of_the_root_element_are_not_checked():
    # js: the validator skips <mjml>, so "validChildren" never runs for it
    mjml_str = '<mjml><mj-button>x</mj-button><mj-body /></mjml>'
    assert _validate(mjml_str) == []


def test_content_of_an_ending_tag_is_not_validated():
    assert _validate(_column('<mj-text>a<div>b</div></mj-text>')) == []


def test_comments_are_skipped():
    inner = '<mj-carousel><!-- a comment --><mj-carousel-image src="x" /></mj-carousel>'
    assert _validate(_column(inner)) == []


def test_unreadable_include_is_reported(tmp_path):
    errors = _validate(_body('<mj-include path="./missing.mjml" />'), template_dir=tmp_path)

    (error,) = errors
    assert error.rule is ValidationRule.INCLUDE_ERROR
