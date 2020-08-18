
from ._base import BodyComponent
from ..helpers import parse_float, parse_int, strip_unit, widthParser
from ..lib import merge_dicts


__all__ = ['MjColumn']

class MjColumn(BodyComponent):

    @classmethod
    def default_attrs(cls):
        return {
            'direction'        : 'ltr',
            'vertical-align'   : 'top',

            # other attrs
            'background-color' : '',
            'border'           : '',
            'border-bottom'    : '',
            'border-left'      : '',
            'border-radius'    : '',
            'border-right'     : '',
            'border-top'       : '',
            'inner-background-color': '',
            'inner-border'     : '',
            'inner-border-bottom': '',
            'inner-border-left': '',
            'inner-border-radius': '',
            'inner-border-right': '',
            'inner-border-top' : '',
            'padding'          : '',
            'padding-bottom'   : '',
            'padding-left'     : '',
            'padding-right'    : '',
            'padding-top'      : '',
            'width'            : '',
            'css-class'        : '',
            # not defined upstream but used?
            'mobileWidth'      : '',
            # not declared but used by MjGroup
            'align'            : '',
        }

    def get_styles(self):
        this = self
        tableStyle = {
            'background-color': this.getAttribute('background-color'),
            'border': this.getAttribute('border'),
            'border-bottom': this.getAttribute('border-bottom'),
            'border-left': this.getAttribute('border-left'),
            'border-radius': this.getAttribute('border-radius'),
            'border-right': this.getAttribute('border-right'),
            'border-top': this.getAttribute('border-top'),
            'vertical-align': this.getAttribute('vertical-align'),
        }
        gutterStyle = {
            'background-color': this.getAttribute('inner-background-color'),
            'border': this.getAttribute('inner-border'),
            'border-bottom': this.getAttribute('inner-border-bottom'),
            'border-left': this.getAttribute('inner-border-left'),
            'border-radius': this.getAttribute('inner-border-radius'),
            'border-right': this.getAttribute('inner-border-right'),
            'border-top': this.getAttribute('inner-border-top'),
        }
        return {
            'div': {
                'font-size': '0px',
                'text-align': 'left',
                'direction': this.getAttribute('direction'),
                'display': 'inline-block',
                'vertical-align': this.getAttribute('vertical-align'),
                'width': this.getMobileWidth(),
            },
            'table': gutterStyle if self.hasGutter() else tableStyle,
            'tdOutlook': {
                'vertical-align': this.getAttribute('vertical-align'),
                'width': this.getWidthAsPixel(),
            },
            'gutter': merge_dicts({
                'padding': this.getAttribute('padding'),
                'padding-top': this.getAttribute('padding-top'),
                'padding-right': this.getAttribute('padding-right'),
                'padding-bottom': this.getAttribute('padding-bottom'),
                'padding-left': this.getAttribute('padding-left'),
                }, tableStyle),
        }

    def getMobileWidth(self):
        containerWidth = self.context['containerWidth']
        nonRawSiblings = self.props['nonRawSiblings']
        width = self.getAttribute('width')
        mobileWidth = self.getAttribute('mobileWidth')
        if mobileWidth != 'mobileWidth':
            return '100%'
        # upstream uses "width === undefined" but we also need to handle width=''
        elif not width:
            return f'{int(100 / nonRawSiblings)}%'

        parsedWidth, unit = widthParser(width, parseFloatToInt=False)
        if unit == '%':
            return width
        return '%s%%' % (parsedWidth / parse_int(containerWidth))

    def getWidthAsPixel(self):
        containerWidth = self.context['containerWidth']
        parsedWidth, unit = widthParser(self.getParsedWidth(True), parseFloatToInt=False)
        if unit == '%':
            px_width = (parse_float(containerWidth) * parsedWidth) / 100
            return f'{px_width}px'
        return f'{parsedWidth}px'


    def render(self):
        this = self
        classesName = f'{this.getColumnClass()} mj-outlook-group-fix'
        css_class = this.getAttribute('css-class')
        if css_class:
            classesName += f' {css_class}'

        div_attrs = self.html_attrs(class_=classesName, style='div')
        column_str = self.renderColumn() if (not self.hasGutter()) else self.renderGutter()
        return f'''<div {div_attrs}>
                {column_str}
            </div>'''

    def getColumnClass(self):
        parsedWidth, unit = self.getParsedWidth()
        formattedClassNb = str(parsedWidth).replace('.', '-')
        if unit == '%':
            className = f'mj-column-per-{formattedClassNb}'
        else:
            # upstream: unit 'px' (+ default)
            className = f'mj-column-px-{formattedClassNb}'

        # Add className to media queries
        addMediaQuery = self.context['addMediaQuery']
        addMediaQuery(className, parsedWidth=parsedWidth, unit=unit)
        return className

    def getParsedWidth(self, toString=False):
        this = self
        nonRawSiblings = this.props['nonRawSiblings']
        width = this.getAttribute('width') or f'{100 / nonRawSiblings}%'

        width_unit = widthParser(width, parseFloatToInt=False)
        if toString:
            return str(width_unit)
        return width_unit

    def getChildContext(self):
        parentWidth = float(strip_unit(self.context['containerWidth']))
        nonRawSiblings = self.props['nonRawSiblings']
        box_widths = self.getBoxWidths()
        borders = box_widths['borders']
        paddings = box_widths['paddings']

        innerBorders = self.getShorthandAttrValue('inner-border', 'left') + \
                       self.getShorthandAttrValue('inner-border', 'right')
        allPaddings = paddings + borders + innerBorders

        containerWidth = self.getAttribute('width') or f'{parentWidth / nonRawSiblings}px'
        parsedWidth, unit = widthParser(containerWidth, parseFloatToInt=False)
        if (unit == '%'):
            containerWidth = f'{(parentWidth * parsedWidth) / 100 - allPaddings}px'
        else:
            width = parsedWidth - allPaddings
            containerWidth = f'{width}px'
        return merge_dicts(self.context, {'containerWidth': containerWidth})


    def hasGutter(self):
        padding_attrs = ('padding', 'padding-bottom', 'padding-left', 'padding-right', 'padding-top')
        attr_values = map(lambda n: self.get_attr(n), padding_attrs)
        return any(filter(lambda v: bool(v), attr_values))

    def renderGutter(self):
        table_attrs = self.html_attrs({
            'border': '0',
            'cellpadding': '0',
            'cellspacing': '0',
            'role': 'presentation',
            'width': '100%',
        })
        return f'''<table {table_attrs}>
            <tbody>
              <tr>
                <td {self.htmlAttributes(style='gutter')}>
                  {self.renderColumn()}
                </td>
              </tr>
            </tbody>
          </table>'''

    def renderColumn(self):
        children = self.props['children']
        def render_child(component):
            if component.isRawElement():
                return component.render()
            td_attrs = component.html_attrs(
                align = component.getAttribute('align'),
                # vertical-align
                class_ = component.getAttribute('css-class'),
                style = {
                    'background': component.getAttribute(
                      'container-background-color',
                    ),
                    'font-size': '0px',
                    'padding': component.getAttribute('padding'),
                    'padding-top': component.getAttribute('padding-top'),
                    'padding-right': component.getAttribute('padding-right'),
                    'padding-bottom': component.getAttribute('padding-bottom'),
                    'padding-left': component.getAttribute('padding-left'),
                    'word-break': 'break-word',
                  },
                **{'vertical-align': component.getAttribute('vertical-align')}
            )
            return f'''<tr>
              <td {td_attrs}>
                {component.render()}
              </td>
            </tr>'''

        table_attrs = self.html_attrs(
            border='0',
            cellpadding='0',
            cellspacing='0',
            role='presentation',
            style='table',
            width='100%',
        )
        return f'''<table {table_attrs}>
            {self.renderChildren(children, renderer=render_child)}
        </table>'''

