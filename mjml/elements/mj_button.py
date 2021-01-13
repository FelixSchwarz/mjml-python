
from ._base import BodyComponent
from ..helpers import widthParser


__all__ = ['MjButton']

class MjButton(BodyComponent):
    @classmethod
    def allowed_attrs(cls):
        return {
            'align'            : 'enum(left,center,right)',
            'background-color' : 'color',
            'border-bottom'    : 'string',
            'border-left'      : 'string',
            'border-radius'    : 'string',
            'border-right'     : 'string',
            'border-top'       : 'string',
            'border'           : 'string',
            'color'            : 'color',
            'container-background-color': 'color',
            'font-family'      : 'string',
            'font-size'        : 'unit(px)',
            'font-style'       : 'string',
            'font-weight'      : 'string',
            'height'           : 'unit(px,%)',
            'href'             : 'string',
            'name'             : 'string',
            'inner-padding'    : 'unit(px,%){1,4}',
            'letter-spacing'   : 'unitWithNegative(px,%)',
            'line-height'      : 'unit(px,%,)',
            'padding-bottom'   : 'unit(px,%)',
            'padding-left'     : 'unit(px,%)',
            'padding-right'    : 'unit(px,%)',
            'padding-top'      : 'unit(px,%)',
            'padding'          : 'unit(px,%){1,4}',
            'rel'              : 'string',
            'target'           : 'string',
            'text-decoration'  : 'string',
            'text-transform'   : 'string',
            'vertical-align'   : 'enum(top,bottom,middle)',
            'text-align'       : 'enum(left,right,center)',
            'width'            : 'unit(px,%)',
            # hidden
            'css-class'        : '',
        }


    @classmethod
    def default_attrs(cls):
        return {
            'align'            : 'center',
            'background-color' : '#414141',
            'border'           : 'none',
            'border-radius'    : '3px',
            'color'            : '#ffffff',
            'font-family'      : 'Ubuntu, Helvetica, Arial, sans-serif',
            'font-size'        : '13px',
            'font-weight'      : 'normal',
            'inner-padding'    : '10px 25px',
            'line-height'      : '120%',
            'padding'          : '10px 25px',
            'target'           : '_blank',
            'text-decoration'  : 'none',
            'text-transform'   : 'none',
            'vertical-align'   : 'middle',
        }


    def get_styles(self):
        this = self
        return {
            'table': {
                'border-collapse': 'separate',
                'width': this.getAttribute('width'),
                'line-height': '100%',
            },
            'td': {
                'border': this.getAttribute('border'),
                'border-bottom': this.getAttribute('border-bottom'),
                'border-left': this.getAttribute('border-left'),
                'border-radius': this.getAttribute('border-radius'),
                'border-right': this.getAttribute('border-right'),
                'border-top': this.getAttribute('border-top'),
                'cursor': 'auto',
                'font-style': this.getAttribute('font-style'),
                'height': this.getAttribute('height'),
                'mso-padding-alt': this.getAttribute('inner-padding'),
                'text-align': this.getAttribute('text-align'),
                'background': this.getAttribute('background-color'),
            },
            'content': {
                'display': 'inline-block',
                'width': this.calculateAWidth(this.getAttribute('width')),
                'background': this.getAttribute('background-color'),
                'color': this.getAttribute('color'),
                'font-family': this.getAttribute('font-family'),
                'font-size': this.getAttribute('font-size'),
                'font-style': this.getAttribute('font-style'),
                'font-weight': this.getAttribute('font-weight'),
                'line-height': this.getAttribute('line-height'),
                'letter-spacing': this.getAttribute('letter-spacing'),
                'margin': '0',
                'text-decoration': this.getAttribute('text-decoration'),
                'text-transform': this.getAttribute('text-transform'),
                'padding': this.getAttribute('inner-padding'),
                'mso-padding-alt': '0px',
                'border-radius': this.getAttribute('border-radius'),
            },
        }


    def calculateAWidth(self, width):
        if not width:
            return None

        parsedWidth, unit = widthParser(width)
        # impossible to handle percents because it depends on padding and text width
        if unit != 'px':
            return None

        _box_widths = self.getBoxWidths()
        borders = _box_widths.borders
        innerPaddings = self.getShorthandAttrValue('inner-padding', 'left') + \
            self.getShorthandAttrValue('inner-padding', 'right')
        width_int = parsedWidth - innerPaddings - borders
        return f'{width_int}px'

    def render(self):
        tag = 'a' if self.getAttribute('href') else 'p'
        tag_attrs = self.html_attrs(
            href   = self.getAttribute('href'),
            rel    = self.getAttribute('rel'),
            name   = self.getAttribute('name'),
            style  = 'content',
            target = self.getAttribute('target') if (tag == 'a') else None,
        )

        table_attrs = self.html_attrs(
            border      = '0',
            cellpadding = '0',
            cellspacing = '0',
            role        = 'presentation',
            style       = 'table',
        )
        bg_color = self.getAttribute('background-color')
        td_bgcolor = None if (bg_color == 'none') else bg_color
        td_attrs = self.html_attrs(
            align   = 'center',
            bgcolor = td_bgcolor,
            role    = 'presentation',
            style   = 'td',
            valign  = self.getAttribute('vertical-align'),
        )
        return f'''
            <table {table_attrs} >
              <tr>
                <td {td_attrs} >
                  <{tag} {tag_attrs} >
                    {self.getContent()}
                  </{tag}>
                </td>
              </tr>
            </table>
        '''
