from mjml.helpers import convertBooleansOnAttrs


def test_converts_boolean_values():
    attrs = {'fluid-on-mobile': 'true', 'full-width': 'false'}
    assert convertBooleansOnAttrs(attrs) == {'fluid-on-mobile': True, 'full-width': False}


def test_only_converts_the_exact_values():
    # the conversion is case-sensitive and does not strip whitespace
    attrs = {
        'alt'  : 'TRUE',
        'title': ' false',
        'name' : 'true story',
        'src'  : '',
    }
    assert convertBooleansOnAttrs(attrs) == attrs


def test_keeps_non_string_values():
    # values from JSON input are not necessarily strings
    attrs = {'width': 600, 'fluid-on-mobile': True, 'alt': None}
    assert convertBooleansOnAttrs(attrs) == attrs
