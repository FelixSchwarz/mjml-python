
from ._base import BodyComponent
from ..helpers import strip_unit, widthParser
from ..lib import merge_dicts


__all__ = ['MjGroup']

class MjGroup(BodyComponent):
    @classmethod
    def default_attrs(cls):
        return {
            'background-color' : '',
            'direction'        : 'ltr',
            'vertical-align'   : '',
            'width'            : '',
            # hidden / used by MjColumn
            'css-class'        : '',
            # NOT declared but used by MjGroup in ".getChildContext()"
            'padding'          : '',
            'padding-left'     : '',
            'padding-right'    : '',
        }

    # js: getStyles()
    def get_styles(self):
        return {
            'div': {
                'font-size'       : '0',
                'line-height'     : '0',
                'text-align'      : 'left',
                'display'         : 'inline-block',
                'width'           : '100%',
                'direction'       : self.getAttribute('direction'),
                'vertical-align'  : self.getAttribute('vertical-align'),
                'background-color': self.getAttribute('background-color'),
            },
            'tdOutlook': {
                'vertical-align'  : self.getAttribute('vertical-align'),
                'width'           : self.getWidthAsPixel(),
            }
        }

    def getChildContext(self):
        parentWidth = float(strip_unit(self.context['containerWidth']))
        nonRawSiblings = self.props['nonRawSiblings']
        children = self.props['children']
        paddingSize = self.getShorthandAttrValue('padding', 'left') + self.getShorthandAttrValue('padding', 'right')

        containerWidth = self.getAttribute('width') or f'{(parentWidth / nonRawSiblings)}px'
        parsedWidth, unit = widthParser(containerWidth, parseFloatToInt=False)

        width_px = None
        if unit == '%':
            width_px = (parentWidth * parsedWidth) / 100 - paddingSize
        else:
            width_px = parsedWidth - paddingSize
        containerWidth = f'{width_px}px'

        return merge_dicts(self.context, {'containerWidth': containerWidth, 'nonRawSiblings': len(children)})

    def getParsedWidth(self, toString=False):
        nonRawSiblings = self.props['nonRawSiblings']
        width = self.getAttribute('width') or f'{100 / nonRawSiblings}%'
        width_unit = widthParser(width, parseFloatToInt=False)
        if toString:
            return str(width_unit)
        return width_unit

    def getWidthAsPixel(self):
        containerWidth = self.context['containerWidth']
        width_str = self.getParsedWidth(toString=True)
        parsedWidth, unit = widthParser(width_str, parseFloatToInt=False)

        if unit == '%':
            width_px = (float(strip_unit(containerWidth)) * parsedWidth) / 100
        else:
            assert unit == 'px'
            width_px = parsedWidth
        return f'{width_px}px'

    def getColumnClass(self):
        parsedWidth, unit = self.getParsedWidth()
        width_int = int(parsedWidth)
        if unit == '%':
            className = f'mj-column-per-{width_int}'
        else:
            # unit: 'px' or anything else (switch/default)
            className = f'mj-column-px-{width_int}'

        # Add className to media queries
        addMediaQuery = self.context['addMediaQuery']
        addMediaQuery(className, parsedWidth=parsedWidth, unit=unit)
        return className

    def render(self):
        children = self.props['children']
        nonRawSiblings = self.props['nonRawSiblings']
        groupWidth = self.getChildContext()['containerWidth']
        containerWidth = self.context['containerWidth']

        def getElementWidth(width):
            if not width:
                containerWidth_int = int(containerWidth)
                nr_non_raw_siblings = int(nonRawSiblings)
                width_px = containerWidth_int / nr_non_raw_siblings
                return f'{width_px}px'

            width_unit = widthParser(width, parseFloatToInt=False)
            if width_unit.unit == '%':
                width_px = (100 * width_unit.parsedWidth) / groupWidth
                return f'{width_px}px'
            return str(width_unit)

        classesName = f'{self.getColumnClass()} mj-outlook-group-fix'
        if self.get_attr('css-class'):
            classesName += f" {self.get_attr('css-class')}"

        container_attrs = self.html_attrs(class_=classesName, style='div')
        table_bgcolor = self.get_attr('background-color')
        table_attrs = self.html_attrs(
            bgcolor     = table_bgcolor if (table_bgcolor != 'none') else None,
            border      = '0',
            cellpadding = '0',
            cellspacing = '0',
            role = 'presentation',
        )

        def child_renderer(component):
            if component.isRawElement():
                return component.render()

            if hasattr(component, 'getWidthAsPixel'):
                width = component.getWidthAsPixel()
            else:
                component.getAttribute('width')
            td_style = {
                'align'         : component.get_attr('align'),
                'vertical-align': component.get_attr('vertical-align'),
                'width'         : getElementWidth(width),
            }
            td_attrs = component.html_attrs(style=td_style)
            return f'''
                <!--[if mso | IE]>
                <td {td_attrs}>
                  <![endif]-->
                    {component.render()}
                  <!--[if mso | IE]>
                  </td>
                  <![endif]-->
            '''

        return f'''<div {container_attrs}>
            <!--[if mso | IE]>
            <table {table_attrs}>
              <tr>
            <![endif]-->
            {self.renderChildren(children, attributes={'mobileWidth': 'mobileWidth'}, renderer=child_renderer)}
            <!--[if mso | IE]>
              </tr>
              </table>
            <![endif]-->
        </div>'''

