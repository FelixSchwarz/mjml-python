from mjml import ValidationRule
from mjml.core.registry import core_components
from mjml.parser import parse_document
from mjml.validator import validate_tree


def _validate(mjml_str, template_dir=None):
    components = core_components()
    tree = parse_document(
        mjml_str, components, template_dir=template_dir, report_include_errors=True
    )
    assert tree is not None
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
    expected = (
        'mj-text cannot be used inside mj-section, only inside: mj-attributes, mj-column, mj-hero'
    )
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


def test_formatted_message_of_a_real_error(tmp_path):
    template = tmp_path / 'template.mjml'
    template.write_text(
        '<mjml>\n  <mj-body>\n    <mj-section>\n'
        '      <mj-column><mj-text color="bogus">hi</mj-text></mj-column>\n'
        '    </mj-section>\n  </mj-body>\n</mjml>'
    )
    components = core_components()
    tree = parse_document(template.read_text(), components, file=str(template))
    assert tree is not None

    (error,) = validate_tree(tree, components)
    expected = (
        f'Line 4 of {template} (mj-text) - '
        'Attribute color has invalid value: bogus for type Color'
    )
    assert error.formatted_message() == expected


def test_formatted_message_names_the_included_file(tmp_path):
    (tmp_path / 'header.mjml').write_text(
        '<mj-section><mj-column><mj-text color="bogus">hi</mj-text></mj-column></mj-section>'
    )
    mjml_str = _body('<mj-include path="./header.mjml" />')

    (error,) = _validate(mjml_str, template_dir=tmp_path)

    included = tmp_path / 'header.mjml'
    # the including template was read from a string, so it has no file name
    assert error.formatted_message() == (
        f'Line 1 of {included}, included at line 1 (mj-text) - '
        'Attribute color has invalid value: bogus for type Color'
    )


def test_unsupported_attribute_says_so_instead_of_illegal():
    inner = '<mj-raw position="file-start">x</mj-raw><mj-section><mj-column /></mj-section>'
    (error,) = _validate(_body(inner))

    assert error.rule is ValidationRule.NOT_IMPLEMENTED
    assert error.message == 'position is not implemented by this port (#74)'


def test_repeated_declaration_in_mj_attributes_is_reported():
    mjml_str = (
        '<mjml><mj-head><mj-attributes>'
        '<mj-text color="red" /><mj-text font-size="20px" />'
        '</mj-attributes></mj-head>'
        '<mj-body><mj-section><mj-column /></mj-section></mj-body></mjml>'
    )
    (error,) = _validate(mjml_str)

    assert error.rule is ValidationRule.NOT_IMPLEMENTED
    assert error.message == 'mj-text is declared more than once.'


def test_different_declarations_in_mj_attributes_are_fine():
    mjml_str = (
        '<mjml>'
          '<mj-head>'
            '<mj-attributes>'
              '<mj-text color="red" />'
              '<mj-button font-size="20px" />'
            '</mj-attributes>'
          '</mj-head>'
          '<mj-body>'
            '<mj-section>'
              '<mj-column />'
            '</mj-section>'
          '</mj-body>'
        '</mjml>'
    )
    assert _validate(mjml_str) == []


def _head(inner):
    return (
        '<mjml>'
          f'<mj-head>{inner}</mj-head>'
          '<mj-body>'
            '<mj-section>'
              '<mj-column>'
                '<mj-text>hi</mj-text>'
              '</mj-column>'
            '</mj-section>'
          '</mj-body>'
        '</mjml>'
    )


def test_an_empty_declaration_in_mj_attributes_is_not_repeated():
    # rendering skips a declaration without attributes, so two of them merge
    # into nothing and produce the same html as upstream
    mjml_str = _head(
        '<mj-attributes><mj-text /><mj-text color="red" /></mj-attributes>'
    )
    assert _validate(mjml_str) == []


def test_declarations_collide_across_mj_attributes_blocks():
    mjml_str = _head(
        '<mj-attributes><mj-text color="red" /></mj-attributes>'
        '<mj-attributes><mj-text font-size="20px" /></mj-attributes>'
    )
    (error,) = _validate(mjml_str)

    assert error.rule is ValidationRule.NOT_IMPLEMENTED
    assert error.message == 'mj-text is declared more than once.'


def test_repeated_mj_font_name_is_reported():
    different = '<mj-font name="A" href="a.css" /><mj-font name="B" href="b.css" />'
    assert _validate(_head(different)) == []

    same = '<mj-font name="Mine" href="one.css" /><mj-font name="Mine" href="two.css" />'
    (error,) = _validate(_head(same))

    assert error.rule is ValidationRule.NOT_IMPLEMENTED
    expected = 'mj-font name="Mine" is declared more than once.'
    assert error.message == expected


def test_repeated_mj_selector_path_is_reported():
    def selector(path, name):
        return (
            f'<mj-selector path="{path}">'
            f'<mj-html-attribute name="{name}">1</mj-html-attribute>'
            '</mj-selector>'
        )

    block = f'<mj-html-attributes>{selector(".x", "a")}{selector(".x", "b")}</mj-html-attributes>'
    (error,) = _validate(_head(block))

    assert error.rule is ValidationRule.NOT_IMPLEMENTED
    expected = 'mj-selector path=".x" is declared more than once.'
    assert error.message == expected


def test_mj_class_declarations_with_the_same_name_are_reported_as_repeated():
    def attributes(inner: str) -> str:
        return (
            '<mjml>'
              '<mj-head>'
                f'<mj-attributes>{inner}</mj-attributes>'
              '</mj-head>'
              '<mj-body>'
                '<mj-section>'
                  '<mj-column />'
                '</mj-section>'
              '</mj-body>'
            '</mjml>'
        )

    different = '<mj-class name="a" color="red" /><mj-class name="b" color="blue" />'
    assert _validate(attributes(different)) == []

    same = '<mj-class name="a" color="red" /><mj-class name="a" font-size="9px" />'
    (error,) = _validate(attributes(same))
    expected = 'mj-class name="a" is declared more than once.'
    assert error.message == expected


def test_an_attribute_which_only_differs_in_case_is_reported():
    # mjml keeps attribute names as written, so "Color" is not "color"
    (error,) = _validate(_column('<mj-text Color="red">hi</mj-text>'))

    assert error.rule is ValidationRule.VALID_ATTRIBUTES
    assert error.message == 'Attribute Color is illegal'
