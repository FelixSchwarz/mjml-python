
import math

from ._base import BodyComponent
from ..helpers import parse_int, strip_unit, widthParser


__all__ = ['MjImage']

class MjImage(BodyComponent):

    @classmethod
    def default_attrs(cls):
        return {
            'align'            : 'center',
            'border'           : '0',
            'height'           : 'auto',
            'padding'          : '10px 25px',
            'target'           : '_blank',
            'font-size'        : '13px',

            # other attrs
            'alt'              : '',
            'border-left'      : '',
            'border-radius'    : '',
            'border-right'     : '',
            # upstream does not declare these (but uses them in getStyles)
            # CHECK LATER: should these be "border-*"?
            'bottom'           : '',
            'left'             : '',
            'right'            : '',
            'top'              : '',
            'container-background-color': '',
            'href'             : '',
            'fluid-on-mobile'  : False,
            'max-height'       : '',
            'padding-bottom'   : '',
            'padding-left'     : '',
            'padding-right'    : '',
            'padding-top'      : '',
            'srcset'           : '',
            'title'            : '',
            'usemap'           : '',
            # not declared upstream but used here
            'full-width'       : '', # enum? ("full-width")
            # not present upstream but used by mj-column
            'vertical-align'   : '',
            'css-class'        : '',
        }

    # js: getStyles()
    def get_styles(self):
        width = self.getContentWidth()
        fullWidth = (self.getAttribute('full-width') == 'full-width')
        width_unit = widthParser(width)

        this = self
        return {
            'img': {
                'border': this.getAttribute('border'),
                'border-left': this.getAttribute('left'),
                'border-right': this.getAttribute('right'),
                'border-top': this.getAttribute('top'),
                'border-bottom': this.getAttribute('bottom'),
                'border-radius': this.getAttribute('border-radius'),
                'display': 'block',
                'outline': 'none',
                'text-decoration': 'none',
                'height': this.getAttribute('height'),
                'max-height': this.getAttribute('max-height'),
                'min-width': '100%' if fullWidth else None,
                'width': '100%',
                'max-width': '100%' if fullWidth else None,
                'font-size': this.getAttribute('font-size'),
            },
            'td': {
                'width': None if fullWidth else str(width_unit),
            },
            'table': {
                'min-width': '100%' if fullWidth else None,
                'max-width': '100%' if fullWidth else None,
                'width': str(width_unit) if fullWidth else None,
                'border-collapse': 'collapse',
                'border-spacing': '0px',
            },
        }

    def getContentWidth(self):
        _width = self.getAttribute('width')
        width = strip_unit(_width) if _width else math.inf
        _box_width = self.getBoxWidths()
        box = _box_width['box']
        return min([box, width])


    def renderImage(self):
        this = self
        height = this.getAttribute('height')
        if height:
            height = height if (height == 'auto') else parse_int(height)

        img_attrs = this.html_attrs(
            alt    = this.getAttribute('alt'),
            height = height,
            src    = this.getAttribute('src'),
            srcset = this.getAttribute('srcset'),
            style  = 'img',
            title  = this.getAttribute('title'),
            width  = this.getContentWidth(),
            usemap = this.getAttribute('usemap'),
        )
        img = f'<img {img_attrs} />'
        href = this.getAttribute('href')
        if href:
            a_attrs = this.htmlAttributes(
                href   = this.getAttribute('href'),
                target = this.getAttribute('target'),
                rel    = this.getAttribute('rel'),
                name   = this.getAttribute('name'),
            )
            return f'<a {a_attrs} >{img}</a>'
        return img

    def headStyle(self, breakpoint):
        # double curly braces used to escape "{" and "}" in f-strings
        return f'''
            @media only screen and (max-width:{breakpoint}) {{
              table.mj-full-width-mobile {{ width: 100% !important; }}
              td.mj-full-width-mobile {{ width: auto !important; }}
            }}'''

    def render(self):
        this = self
        fluid_cls = 'mj-full-width-mobile' if this.getAttribute('fluid-on-mobile') else None
        table_attrs = this.html_attrs(
            border      = '0',
            cellpadding = '0',
            cellspacing = '0',
            role        = 'presentation',
            style       = 'table',
            class_      = fluid_cls,
        )
        td_attrs = this.html_attrs(
            style       = 'td',
            class_      = fluid_cls,
        )
        return f'''
          <table {table_attrs} >
            <tbody>
              <tr>
                <td {td_attrs} >
                  {this.renderImage()}
                </td>
              </tr>
            </tbody>
          </table>'''

