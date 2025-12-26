from mjml.elements._accordion_helpers import resolve_accordion_font_family


def test_resolve_accordion_font_family_can_use_value_from_rawAttrs():
    props = {
        'rawAttrs': {'font-family': 'Arial'},
    }
    context = {
        'accordionFontFamily': 'Ubuntu',
        'elementFontFamily': 'Roboto',
    }

    assert resolve_accordion_font_family(props, context, fallback='Open Sans') == 'Arial'


def test_resolve_accordion_font_family_can_use_value_from_context():
    props = {'rawAttrs': {}}
    context = {
        'elementFontFamily': 'Roboto',
        'accordionFontFamily': 'Ubuntu',
    }
    assert resolve_accordion_font_family(props, context, fallback='Open Sans') == 'Roboto'



def test_resolve_accordion_font_family_inheritance():
    """When no elementFontFamily, inherit from accordion parent."""
    props = {'rawAttrs': {}}
    context = {
        'accordionFontFamily': 'Ubuntu',  # From parent mj-accordion
    }
    assert resolve_accordion_font_family(props, context, fallback='Open Sans') == 'Ubuntu'


def test_resolve_accordion_font_family_uses_fallback_when_no_explicit_value_is_set():
    """When no context font, use the default attribute."""
    props = {
        'rawAttrs': {},
    }
    assert resolve_accordion_font_family(props, context={}, fallback='Open Sans') == 'Open Sans'


def test_resolve_accordion_font_family_priority():
    context = {
        'elementFontFamily': 'Roboto',
        'accordionFontFamily': 'Ubuntu',
    }
    # elementFontFamily should win over accordionFontFamily
    props = {'rawAttrs': {}}
    assert resolve_accordion_font_family(props, context, fallback='Open Sans') == 'Roboto'

    # explicit font-family should win over elementFontFamily
    props = {'rawAttrs': {'font-family': 'Arial'}}
    assert resolve_accordion_font_family(props, context, fallback='Liberation Sans') == 'Arial'
