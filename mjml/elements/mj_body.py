
from ..lib import merge_dicts
from ._base import BodyComponent


__all__ = ['MjBody']

class MjBody(BodyComponent):
    component_name = 'mj-body'

    @classmethod
    def allowed_attrs(cls):
        return {
            'background-color': '',
            'css-class'       : None,
        }

    @classmethod
    def default_attrs(cls):
        return {
            'width'           : '600px',
        }

    def get_styles(self):
        return {
            'div': {
                'background-color': self.get_attr('background-color'),
            },
        }

    def getChildContext(self):
        return merge_dicts(
            self.context,
            {'containerWidth': self.get_attr('width')}
        )

    def render(self):
        setBackgroundColor = self.context['setBackgroundColor']
        setBackgroundColor(self.get_attr('background-color'))

        globalData = self.context.get('globalData', {})
        attrs = {
            'aria-roledescription': 'email',
            'class': self.get_attr('css-class'),
            'style': 'div',
            'role': 'article',
            'lang': globalData.get('lang') or self.context.get('lang'),
            'dir': globalData.get('dir_') or self.context.get('dir_'),
        }
        title = globalData.get('title')
        if title:
            attrs['aria-label'] = title
        html_attrs = self.html_attrs(**attrs)
        children_str = self.renderChildren()
        return f'<div {html_attrs}>{children_str}</div>'
