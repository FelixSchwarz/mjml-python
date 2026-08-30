import pytest

from mjml.core.registry import register_core_components
from mjml.core.types import initialize_type


def is_valid(type_config, value):
    return initialize_type(type_config).is_valid(value)


def test_returns_the_same_type_instance_for_a_declaration():
    assert initialize_type('unit(px,%)') is initialize_type('unit(px,%)')


def test_raises_for_declarations_without_a_type():
    # attributes declared without a type (e.g. "css-class") must never reach
    # initialize_type()
    with pytest.raises(ValueError):
        initialize_type('')
    with pytest.raises(ValueError):
        initialize_type('nonexistent')


def test_boolean_only_accepts_real_booleans():
    assert is_valid('boolean', True)
    assert is_valid('boolean', False)
    # "true" and "false" are converted to booleans before validation
    assert not is_valid('boolean', 'true')
    assert not is_valid('boolean', 'false')
    assert not is_valid('boolean', 'yes')
    assert not is_valid('boolean', '')


@pytest.mark.parametrize('value', [
    '#abc',
    '#AABBCC',
    'red',
    'transparent',
    'inherit',
    'rgb(255,0,0)',
    'rgb(255, 0, 0)',
    'rgba(255, 0, 0, 0.5)',
    'RGBA(255,0,0,0.5)',
])
def test_color_accepts_valid_colors(value):
    assert is_valid('color', value)


@pytest.mark.parametrize('value', [
    '#ab',
    '#abcd',
    'bogus',
    # color names are case-sensitive
    'RED',
])
def test_color_rejects_invalid_colors(value):
    assert not is_valid('color', value)


@pytest.mark.parametrize('value', ['xx rgb(1,2,3) yy', 'garbage rgba(1,2,3,0.5)'])
def test_color_rejects_values_which_only_contain_a_color(value):
    # mjml JS accepts these, it searches for a color anywhere in the value
    assert not is_valid('color', value)


def test_color_expands_shorthand_notation():
    color = initialize_type('color')
    assert color.normalized_value('#abc') == '#aabbcc'
    assert color.normalized_value('#aabbcc') == '#aabbcc'
    assert color.normalized_value('red') == 'red'
    # values from JSON input are not necessarily strings
    assert color.normalized_value(42) == 42


def test_enum_only_accepts_the_declared_values():
    assert is_valid('enum(left,right,center)', 'left')
    assert is_valid('enum(left,right,center)', 'center')
    assert not is_valid('enum(left,right,center)', 'top')
    # the matchers are anchored, so a partial value is invalid
    assert not is_valid('enum(left,right,center)', 'lef')
    assert not is_valid('enum(left,right,center)', 'left right')


def test_enum_can_declare_an_empty_value():
    # "mj-section" declares full-width as "enum(full-width,false,)"
    assert is_valid('enum(full-width,false,)', 'full-width')
    assert is_valid('enum(full-width,false,)', '')
    assert not is_valid('enum(full-width,false,)', 'true')


def test_integer_accepts_numbers():
    assert is_valid('integer', '0')
    assert is_valid('integer', '42')


@pytest.mark.parametrize('value', ['abc5', '5abc'])
def test_integer_rejects_values_which_only_contain_a_number(value):
    # mjml JS accepts these, it searches for a number anywhere in the value
    assert not is_valid('integer', value)


def test_integer_rejects_non_numbers():
    assert not is_valid('integer', 'abc')
    assert not is_valid('integer', '')
    # mjml JS accepts "4.2" as an integer
    assert not is_valid('integer', '4.2')


def test_string_accepts_everything():
    assert is_valid('string', 'foo')
    assert is_valid('string', '')
    assert is_valid('string', '1px solid #abc')


@pytest.mark.parametrize('value', ['10px', '1.5px', '.5px', '0', '20%'])
def test_unit_accepts_a_single_value(value):
    assert is_valid('unit(px,%)', value)


def test_unit_rejects_unknown_units():
    assert not is_valid('unit(px,%)', '10em')
    assert not is_valid('unit(px)', '10%')
    assert not is_valid('unit(px,%)', '10')


def test_unit_can_declare_an_empty_unit():
    # the empty unit allows bare numbers, e.g. for "mj-image width"
    assert is_valid('unit(px,%,)', '10')
    assert is_valid('unit(px,%,)', '10px')


def test_unit_can_accept_auto():
    assert is_valid('unit(px,%,auto)', 'auto')
    assert is_valid('unit(px,%,auto)', '10px')
    assert not is_valid('unit(px,%)', 'auto')


@pytest.mark.parametrize('value', ['10px', '10px 20px', '10px 20px 30px 40px'])
def test_unit_accepts_shorthand_values(value):
    assert is_valid('unit(px,%){1,4}', value)


def test_unit_rejects_more_values_than_declared():
    assert not is_valid('unit(px,%)', '10px 20px')
    assert not is_valid('unit(px,%){1,4}', '10px 20px 30px 40px 50px')


@pytest.mark.parametrize('value', ['1,2px', '..px', '1.2.3px', '10px,20px'])
def test_unit_rejects_malformed_numbers(value):
    # mjml JS accepts these, it does not require a real number before the unit
    assert not is_valid('unit(px,%){1,4}', value)


@pytest.mark.parametrize('value', ['-1px', '1em', '-.5em', '0'])
def test_unit_with_negative_accepts_negative_values(value):
    assert is_valid('unitWithNegative(px,em)', value)


@pytest.mark.parametrize('value', ['-,px', '--1px'])
def test_unit_with_negative_rejects_malformed_numbers(value):
    # mjml JS accepts these, it allows "-" anywhere in the number
    assert not is_valid('unitWithNegative(px,em)', value)


def test_no_error_message_for_valid_values():
    assert initialize_type('color').error_message('red') is None


def test_error_message_names_the_type():
    assert initialize_type('color').error_message('bogus') == (
        'has invalid value: bogus for type Color'
    )
    assert initialize_type('boolean').error_message('yes') == (
        'has invalid value: yes for type Boolean'
    )
    assert initialize_type('integer').error_message('abc') == (
        'has invalid value: abc for type Integer'
    )
    # a boolean value is shown as it was written in the template
    assert initialize_type('color').error_message(True) == (
        'has invalid value: true for type Color'
    )


def test_error_message_for_enum_lists_the_accepted_values():
    assert initialize_type('enum(left,right)').error_message('top') == (
        'has invalid value: top for type Enum, only accepts left, right'
    )


def test_error_message_for_unit_lists_units_and_number_of_values():
    assert initialize_type('unit(px,%)').error_message('10em') == (
        'has invalid value: 10em for type Unit, only accepts (px, %) units and 1 value(s)'
    )
    assert initialize_type('unit(px,%){1,4}').error_message('10em') == (
        'has invalid value: 10em for type Unit, only accepts (px, %) units and 1 to 4 value(s)'
    )


def test_every_declared_attribute_has_a_known_type():
    # an attribute declared without a type can never be validated
    undeclared = []
    for component_name, component_cls in sorted(register_core_components().items()):
        for attr_name, type_config in component_cls.allowed_attrs().items():
            try:
                initialize_type(type_config)
            except ValueError:
                undeclared.append(f'{component_name} {attr_name}={type_config!r}')
    assert not undeclared
