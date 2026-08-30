
from mjml.elements._base import BodyComponent
from mjml.helpers import buildPreview


__all__ = ['MjBody']

class MjBody(BodyComponent):
    component_name = 'mj-body'

    @classmethod
    def allowed_attrs(cls):
        return {
            'background-color': 'color',
            'width'           : 'unit(px)',
            'css-class'       : 'string',
            'id'              : 'string',
        }

    @classmethod
    def default_attrs(cls):
        return {
            'width'           : '600px',
        }

    def get_styles(self):
        background_color = self.get_attr('background-color')
        return {
            'body': {
                'word-spacing'    : 'normal',
                'background-color': background_color,
            },
            'div': {
                'word-spacing'    : 'normal',
                'background-color': background_color,
            },
        }

    def getChildContext(self):
        return {**self.context, 'containerWidth': self.get_attr('width')}

    def render(self):
        globalData = self.context.get('globalData', {})
        body_attrs = self.html_attrs(**{
            'id'   : self.get_attr('id'),
            'class_': self.get_attr('css-class'),
            'style': 'body',
        })
        div_attrs = {}
        title = globalData.get('title')
        if title:
            div_attrs['aria-label'] = title
        div_attrs.update({
            'aria-roledescription': 'email',
            'role': 'article',
            'lang': globalData.get('lang') or self.context.get('lang'),
            'dir': globalData.get('dir_') or self.context.get('dir_'),
            'style': 'div',
        })
        preview_str = buildPreview(globalData.get('preview'))
        children_str = self.renderChildren()
        return (
            f'<body {body_attrs}>'
            f'{preview_str}'
            f'<div {self.html_attrs(**div_attrs)}>{children_str}</div>'
            '</body>'
        )
