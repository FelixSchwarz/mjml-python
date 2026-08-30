import re
from collections.abc import Iterator


__all__ = ['remove_important_from_inlined_styles']

_STYLE_ATTR = re.compile(r'''style\s*=\s*(?:"([^"]*)"|'([^']*)')''')
# js: Juice.removeImportant() only strips "!important" at the end of a value
_IMPORTANT = re.compile(r'\s*!important(?=\s*(?:;|$))')


def remove_important_from_inlined_styles(html: str, inlined_html: str) -> str:
    """
    Return the CSS-inlined HTML without "!important" in all "style" attributes
    which were modified by the CSS inliner.

    Juice (used by the JS implementation) drops "!important" when it merges CSS
    declarations into a "style" attribute - even for declarations which were
    present in that attribute before. However it leaves the attribute untouched
    if no CSS rule matched the element. "css_inline" keeps "!important" so it
    has to be removed afterwards.
    """
    unmodified_values = frozenset(_style_attr_values(html))

    def _remove_important(match: re.Match) -> str:
        value = _matched_value(match)
        if value in unmodified_values:
            # the CSS inliner did not touch this attribute (e.g. because the
            # element is inside a conditional comment for Outlook)
            return match.group(0)
        return f'style="{_IMPORTANT.sub("", value)}"'

    return _STYLE_ATTR.sub(_remove_important, inlined_html)


def _style_attr_values(html: str) -> Iterator[str]:
    for match in _STYLE_ATTR.finditer(html):
        yield _matched_value(match)

def _matched_value(match: re.Match) -> str:
    double_quoted = match.group(1)
    return double_quoted if (double_quoted is not None) else match.group(2)
