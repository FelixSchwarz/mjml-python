
from ._base import BodyComponent
from .mj_text import stringify_element
from ..helpers import widthParser


__all__ = ['MjTable']

class MjTable(BodyComponent):
    @classmethod
    def allowed_attrs(cls):
        return {
            'align'            : 'enum(left,right,center)',
            'border'           : 'string',
            'cellpadding'      : 'integer',
            'cellspacing'      : 'integer',
            'container-background-color': 'color',
            'color'            : 'color',
            'font-family'      : 'string',
            'font-size'        : 'unit(px)',
            'font-weight'      : 'string',
            'line-height'      : 'unit(px,%,)',
            'padding-bottom'   : 'unit(px,%)',
            'padding-left'     : 'unit(px,%)',
            'padding-right'    : 'unit(px,%)',
            'padding-top'      : 'unit(px,%)',
            'padding'          : 'unit(px,%){1,4}',
            'table-layout'     : 'enum(auto,fixed,initial,inherit)',
            'vertical-align'   : 'enum(top,bottom,middle)',
            'width'            : 'unit(px,%)',
            # hidden / used by MjColumn
            'css-class'        : '',
        }

    @classmethod
    def default_attrs(cls):
        return {
            'align'            : 'left',
            'border'           : 'none',
            'cellpadding'      : '0',
            'cellspacing'      : '0',
            'color'            : '#000000',
            'font-family'      : 'Ubuntu, Helvetica, Arial, sans-serif',
            'font-size'        : '13px',
            'line-height'      : '22px',
            'padding'          : '10px 25px',
            'table-layout'     : 'auto',
            'width'            : '100%',
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

