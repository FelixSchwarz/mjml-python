
from ._head_base import HeadComponent


__all__ = ['MjStyle']

class MjStyle(HeadComponent):
    component_name = 'mj-style'

    @classmethod
    def default_attrs(cls):
        return {
            'inline': '',
        }

    def handler(self):
        add = self.context['add']
        inline_attr = 'inlineStyle' if (self.get_attr('inline') == 'inline') else 'style'
        html_str = self.getContent()
        # CSS can contain child selectors (e.g. "h1 > p") beautifulsoup only
        # returns escaped entities. To make these selectors work, we need to
        # unescape these.
        css_str = html_str.replace('&gt;', '>')
        add(inline_attr, css_str)
