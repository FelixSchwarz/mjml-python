from mjml.helpers import formatAttributes


ALLOWED_ATTRS = {
    'color'           : 'color',
    'background-color': 'color',
    'border'          : 'string',
    'css-class'       : None,
}


def test_expands_shorthand_color():
    attrs = {'color': '#abc', 'background-color': '#F0F'}
    assert formatAttributes(attrs, ALLOWED_ATTRS) == {
        'color': '#aabbcc',
        'background-color': '#FF00FF',
    }


def test_keeps_other_color_notations():
    attrs = {
        'color'           : '#aabbcc',
        'background-color': 'rgba(255, 0, 0, 0.5)',
    }
    assert formatAttributes(attrs, ALLOWED_ATTRS) == attrs

    assert formatAttributes({'color': 'red'}, ALLOWED_ATTRS) == {'color': 'red'}
    assert formatAttributes({'color': ''}, ALLOWED_ATTRS) == {'color': ''}


def test_ignores_attributes_which_are_not_declared_as_color():
    # a shorthand color inside a "string" attribute must be left alone
    attrs = {'border': '1px solid #abc', 'css-class': '#abc'}
    assert formatAttributes(attrs, ALLOWED_ATTRS) == attrs

    # attributes which are not declared at all (e.g. only present in
    # "default_attrs()") are passed through as well
    assert formatAttributes({'ico-color': '#abc'}, ALLOWED_ATTRS) == {'ico-color': '#abc'}
    assert formatAttributes({'color': '#abc'}, {}) == {'color': '#abc'}


def test_ignores_non_string_values():
    # values from JSON input are not necessarily strings
    attrs = {'color': 42, 'background-color': None}
    assert formatAttributes(attrs, ALLOWED_ATTRS) == attrs
