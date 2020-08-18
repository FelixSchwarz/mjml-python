
from ._base import BodyComponent
from ..helpers import parse_int, widthParser
from ..lib import merge_dicts


__all__ = ['MjDivider']

class MjDivider(BodyComponent):

    @classmethod
    def default_attrs(cls):
        return {
            'border-color'     : '#000000',
            'border-style'     : 'solid',
            'border-width'     : '4px',
            'padding'          : '10px 25px',
            'width'            : '100%',

            # other attrs
            'container-background-color': '',
            'padding-bottom'   : '',
            'padding-left'     : '',
            'padding-right'    : '',
            'padding-top'      : '',
            # hidden / used by MjColumn
            'align'            : '',
            'vertical-align'   : '',
            'css-class'        : '',
        }

    def get_styles(self):
        _t = tuple
        border_attrs = _t(map(lambda k: self.get_attr(f'border-{k}'), ['style', 'width', 'color']))
        border_attr_str = ' '.join(border_attrs)
        p = {
            'border-top': border_attr_str,
            'font-size' : '1px',
            'margin'    : '0px auto',
            'width'     : self.getAttribute('width'),
        }
        return {
            'p': p,
            'outlook': merge_dicts(p, {'width': self.getOutlookWidth()}),
        }

    def getOutlookWidth(self):
        this = self
        containerWidth = this.context['containerWidth']
        paddingSize = this.getShorthandAttrValue('padding', 'left') + this.getShorthandAttrValue('padding', 'right')
        width = this.getAttribute('width')
        parsedWidth, unit = widthParser(width)

        if unit == '%':
            px = (parse_int(containerWidth) * parse_int(parsedWidth)) / 100 - paddingSize
            return f'{px}px'
        elif unit == 'px':
            return width
        px = parse_int(containerWidth) - paddingSize
        return f'{px}px'

    def renderAfter(self):
        table_attrs = self.html_attrs(
            align       = 'center',
            border      = '0',
            cellpadding = '0',
            cellspacing = '0',
            style       = 'outlook',
            role        = 'presentation',
            width        = self.getOutlookWidth(),
        )
        return f'''
            <!--[if mso | IE]>
            <table {table_attrs} >
                <tr>
                  <td style="height:0;line-height:0;">
                    &nbsp;
                  </td>
                </tr>
              </table>
            <![endif]-->'''

    def render(self):
        return f'''
            <p {self.html_attrs(style='p')} > </p>
            {self.renderAfter()}
        '''

