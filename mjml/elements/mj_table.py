
import re

from ..helpers import widthParser
from ._base import BodyComponent


__all__ = ['MjTable']

class MjTable(BodyComponent):
    component_name = 'mj-table'

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
            'role'             : 'enum(none,presentation)',
            'table-layout'     : 'enum(auto,fixed,initial,inherit)',
            'vertical-align'   : 'enum(top,bottom,middle)',
            'width'            : 'unit(px,%,auto)',
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
        has_cellspacing = self.hasCellspacing()
        return {
            'table': {
                'color'       : self.get_attr('color'),
                'font-family' : self.get_attr('font-family'),
                'font-size'   : self.get_attr('font-size'),
                'line-height' : self.get_attr('line-height'),
                'table-layout': self.get_attr('table-layout'),
                'width'       : self.get_attr('width'),
                'border'      : self.get_attr('border'),
                'border-collapse': 'separate' if has_cellspacing else None,
            },
        }

    def getWidth(self):
        width = self.get_attr('width')
        if width == 'auto':
            return width
        parsedWidth, unit = widthParser(width)
        return width if (unit == '%') else parsedWidth

    def hasCellspacing(self):
        cellspacing = self.get_attr('cellspacing')
        numeric_value = re.sub(r'[^\d.]', '', str(cellspacing))
        match = re.match(r'(?:\d+\.?\d*|\.\d+)', numeric_value)
        return bool(match) and float(match.group()) > 0

    def render(self):
        table_attrs = self.html_attrs(
            width  = self.getWidth(),
            border = '0',
            style  = 'table',
            cellpadding = self.get_attr('cellpadding'),
            cellspacing = self.get_attr('cellspacing'),
            role        = self.get_attr('role'),
        )
        content_html = self.getContent()
        return f'''<table {table_attrs}>
            {content_html}
        </table>'''
