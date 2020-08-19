
from ._base import BodyComponent
from .mj_text import stringify_element
from ..helpers import widthParser


__all__ = ['MjTable']

class MjTable(BodyComponent):
    @classmethod
    def default_attrs(cls):
        return {
            'align'         : 'left',
            'border'        : 'none',
            'cellpadding'   : '0',
            'cellspacing'   : '0',
            'color'         : '#000000',
            'container-background-color': '',
            'font-family'   : 'Ubuntu, Helvetica, Arial, sans-serif',
            'font-size'     : '13px',
            'line-height'   : '22px',
            'padding'       : '10px 25px',
            'padding-bottom': '',
            'padding-left'  : '',
            'padding-right' : '',
            'padding-top'   : '',
            'table-layout'  : 'auto',
            'width'         : '100%',
            'vertical-align': '',
            # hidden / used by MjColumn
            'css-class'        : '',
        }

    # js: getStyles()
    def get_styles(self):
        return {
            'table': {
                'color'       : self.get_attr('color'),
                'font-family' : self.get_attr('font-family'),
                'font-size'   : self.get_attr('font-size'),
                'line-height' : self.get_attr('line-height'),
                'table-layout': self.get_attr('table-layout'),
                'width'       : self.get_attr('width'),
                'border'      : self.get_attr('border'),
            },
        }

    def getWidth(self):
        width = self.get_attr('width')
        parsedWidth, unit = widthParser(width)
        return width if (unit == '%') else parsedWidth

    def render(self):
        table_attrs = self.html_attrs(
            width  = self.getWidth(),
            border = '0',
            style  = 'table',
            cellpadding = self.get_attr('cellpadding'),
            cellspacing = self.get_attr('cellspacing'),
        )
        children_html = ''
        for child in self.children:
            children_html += stringify_element(child)
        content_html = self.getContent() + children_html
        return f'''<table {table_attrs}>
            {content_html}
        </table>'''

