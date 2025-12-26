from typing import ClassVar

from typing_extensions import override

from ._head_base import HeadComponent


__all__ = ['MjStyle']

class MjStyle(HeadComponent):
    component_name: ClassVar[str] = 'mj-style'

    @override
    @classmethod
    def default_attrs(cls) -> dict[str, str]:
        return {
            'inline': '',
        }

    @override
    def handler(self) -> None:
        add = self.context['add']
        inline_attr = 'inlineStyle' if (self.get_attr('inline') == 'inline') else 'style'
        html_str = self.getContent()
        # CSS can contain child selectors (e.g. "h1 > p") beautifulsoup only
        # returns escaped entities. To make these selectors work, we need to
        # unescape these.
        css_str = html_str.replace('&gt;', '>')
        add(inline_attr, css_str)
