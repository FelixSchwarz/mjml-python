
from ._head_base import HeadComponent


__all__ = ['MjStyle']

class MjStyle(HeadComponent):
    @classmethod
    def default_attrs(cls):
        return {
            'inline'            : '',
        }

    def handler(self):
        add = self.context['add']
        inline_attr = 'inlineStyle' if (self.get_attr('inline') == 'inline') else 'style'
        add(inline_attr, self.getContent())

