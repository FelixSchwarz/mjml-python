
from typing import Mapping, Optional


__all__ = ['resolve_accordion_font_family']

def resolve_accordion_font_family(
    props: Mapping[str, Optional[Mapping[str, str]]],
    context: Mapping[str, Optional[str]],
    fallback: str,
) -> str:
    """
    Resolve font-family for accordion child components (title/text).

    Priority:
    1. Explicitly set font-family on the element
    2. elementFontFamily from context
    3. accordionFontFamily from context (inherited from parent mj-accordion)
    4. Default attribute value
    """
    _raw_attrs = props.get('rawAttrs') or {}
    if 'font-family' in _raw_attrs:
        _font_family = _raw_attrs['font-family']
    elif context.get('elementFontFamily'):
        _font_family = context['elementFontFamily']
    elif context.get('accordionFontFamily'):
        _font_family = context['accordionFontFamily']
    else:
        _font_family = None
    return _font_family or fallback
