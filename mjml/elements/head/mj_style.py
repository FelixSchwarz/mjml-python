import typing as t

import typing_extensions as te

from ._head_base import HeadComponent


__all__ = ['MjStyle']

class MjStyle(HeadComponent):
    component_name: t.ClassVar[str] = 'mj-style'

    @te.override
    @classmethod
    def default_attrs(cls) -> t.Dict[str, str]:
        return {
            'inline': '',
        }

    @te.override
    def handler(self) -> None:
        add = self.context['add']
        inline_attr = 'inlineStyle' if (self.get_attr('inline') == 'inline') else 'style'
        html_str = self.getContent()
        # CSS can contain child selectors (e.g. "h1 > p") beautifulsoup only
        # returns escaped entities. To make these selectors work, we need to
        # unescape these.
        css_str = html_str.replace('&gt;', '>')
        add(inline_attr, css_str)
