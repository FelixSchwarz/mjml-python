
import math
from collections import namedtuple
from typing import Literal, Union, overload

from mjml.core import ComponentCategory
from mjml.helpers import WidthUnit, parse_float, parse_int, strip_unit, widthParser

from ._base import BodyComponent


__all__ = ['MjColumn']

# js: { top, right, bottom, left }
Padding = namedtuple('Padding', ('top', 'right', 'bottom', 'left'))

class MjColumn(BodyComponent):
    component_name = 'mj-column'
    categories = frozenset({ComponentCategory.COLUMN_LEVEL})
    accepts = frozenset({ComponentCategory.BODY_ELEMENT, ComponentCategory.RAW})

    @classmethod
    def allowed_attrs(cls):
        return {
            'background-color': 'color',
            'border'          : 'string',
            'border-bottom'   : 'string',
            'border-left'     : 'string',
            'border-radius'   : 'string',
            'border-right'    : 'string',
            'border-top'      : 'string',
            'direction'       : 'enum(ltr,rtl)',
            'inner-background-color': 'color',
            'padding-bottom'  : 'unit(px,%)',
            'padding-left'    : 'unit(px,%)',
            'padding-right'   : 'unit(px,%)',
            'padding-top'     : 'unit(px,%)',
            'inner-border'    : 'string',
            'inner-border-bottom': 'string',
            'inner-border-left'  : 'string',
            'inner-border-radius': 'string',
            'inner-border-right' : 'string',
            'inner-border-top': 'string',
            'padding'         : 'unit(px,%){1,4}',
            'vertical-align'  : 'enum(top,bottom,middle)',
            'width'           : 'unit(px,%)',
        }

    @classmethod
    def default_attrs(cls):
        return {
            'direction'       : 'ltr',
            'vertical-align'  : 'top',

            # other attrs
            # not defined upstream but used?
            'mobileWidth'     : '',
            # not declared but used by MjGroup
            'align'           : None,
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
                **self.getMobileGutterStyles(),
            },
            'table': gutterStyle if self.hasGutter() else tableStyle,
            'tdOutlook': {
                'vertical-align': this.getAttribute('vertical-align'),
                'width': this.getWidthAsPixel(),
                **self.getOutlookGutterStyles(),
            },
            'gutter': {
                'padding': this.getAttribute('padding'),
                'padding-top': this.getAttribute('padding-top'),
                'padding-right': this.getAttribute('padding-right'),
                'padding-bottom': this.getAttribute('padding-bottom'),
                'padding-left': this.getAttribute('padding-left'),
                **tableStyle,
            },
        }

    def getMobileWidth(self):
        containerWidth = self.context['containerWidth']
        nonRawSiblings = self.props['nonRawSiblings']
        width = self.getAttribute('width')
        mobileWidth = self.getAttribute('mobileWidth')
        if mobileWidth != 'mobileWidth':
            return '100%'
        # Group columns don't stack on mobile so they use the gutter-reduced
        # desktop width.
        elif self.context.get('isInGroup') and self.hasColumnGutter():
            parsedWidth, unit = self.getDesktopWidth()
            if unit == '%':
                return f'{parsedWidth}%'
            return f'{normalize_unit_value((parsedWidth / parse_int(containerWidth)) * 100)}%'
        # upstream uses "width === undefined" but we also need to handle width=''
        elif not width:
            return f'{int(100 / nonRawSiblings)}%'

        parsedWidth, unit = widthParser(width, parseFloatToInt=False)
        if unit == '%':
            return width
        return f'{normalize_unit_value((parsedWidth / parse_int(containerWidth)) * 100)}%'


    def getWidthAsPixel(self):
        containerWidth = self.context['containerWidth']
        parsedWidth, unit = widthParser(self.getParsedWidth(toString=True), parseFloatToInt=False)
        if unit == '%':
            px_width = (parse_float(containerWidth) * parsedWidth) / 100
            return f'{js_like_rounding(px_width)}px'
        return f'{js_like_rounding(parsedWidth)}px'


    def render(self):
        this = self
        classesName = this.getColumnClass()
        if this.hasColumnGutter():
            classesName += f' {this.getDesktopGutterClassName()}'
        classesName += ' mj-outlook-group-fix'
        css_class = this.getAttribute('css-class')
        if css_class:
            classesName += f' {css_class}'

        div_attrs = self.html_attrs(class_=classesName, style='div')
        column_str = self.renderColumn() if (not self.hasGutter()) else self.renderGutter()
        return f'''<div {div_attrs}>
                {column_str}
            </div>'''

    def getColumnClass(self):
        has_column_gutter = self.hasColumnGutter()
        if has_column_gutter:
            parsedWidth, unit = self.getDesktopWidth()
        else:
            parsedWidth, unit = self.getParsedWidth()
        if unit == 'px':
            parsedWidth = js_like_rounding(parsedWidth)
        formattedClassNb = str(parsedWidth).replace('.', '-')
        if unit == '%':
            className = f'mj-column-per-{formattedClassNb}'
        else:
            # upstream: unit 'px' (+ default)
            className = f'mj-column-px-{formattedClassNb}'

        # Add className to media queries
        addMediaQuery = self.context['addMediaQuery']
        addMediaQuery(className, parsedWidth=parsedWidth, unit=unit)
        # Group columns already carry the gutter padding inline so we must not
        # emit duplicate media query rules for them.
        if has_column_gutter and not self.context.get('isInGroup'):
            addMediaQuery(
                self.getDesktopGutterClassName(),
                padding=self.getDesktopPadding(),
            )
        return className

    @overload
    def getParsedWidth(self, toString: Literal[False]=False) -> WidthUnit: ...

    @overload
    def getParsedWidth(self, toString: Literal[True]) -> str: ...

    @overload
    def getParsedWidth(self, toString: bool) -> Union[WidthUnit, str]: ...

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
        return {**self.context, 'containerWidth': containerWidth}


    def hasColumnGutter(self):
        """Whether the enclosing "mj-section" sets a "gutter" (!= ".hasGutter()"
        which tells if this column has a padding of its own)."""
        gutter = self.context.get('gutter')
        return (gutter is not None) and (gutter != '')

    def getNormalizedGutterValue(self, targetUnit: str) -> Union[int, float]:
        gutter = self.context.get('gutter')
        if not gutter:
            return 0

        containerWidth = self.context['containerWidth']
        parsedWidth, unit = widthParser(gutter, parseFloatToInt=False)
        if unit == targetUnit:
            return parsedWidth
        elif (targetUnit == '%') and (unit == 'px'):
            return (parsedWidth / parse_float(containerWidth)) * 100
        elif (targetUnit == 'px') and (unit == '%'):
            return (parse_float(containerWidth) * parsedWidth) / 100
        return parsedWidth

    def getDesktopUnit(self) -> str:
        return self.getParsedWidth().unit

    def getDesktopWidth(self) -> WidthUnit:
        """Column width reduced by its share of the gutter."""
        sibling = self.props['sibling']
        index = self.props['index']
        parsedWidth, unit = self.getParsedWidth()

        if not self.hasColumnGutter():
            if unit == 'px':
                parsedWidth = js_like_rounding(parsedWidth)
            return WidthUnit(width=parsedWidth, unit=unit)

        gutter = self.getNormalizedGutterValue(unit)
        reduction = (gutter * (sibling - 1)) / sibling
        reducedWidth = max(0, normalize_unit_value(parsedWidth - reduction))

        if unit != 'px':
            return WidthUnit(width=reducedWidth, unit=unit)

        # Distribute the leftover pixels to the leading columns so that the
        # column widths add up to the container width again.
        floorWidth = math.floor(reducedWidth)
        fractional = reducedWidth - floorWidth
        extraPixels = max(0, min(sibling, js_like_rounding(sibling * fractional)))
        return WidthUnit(width=floorWidth + (1 if (index < extraPixels) else 0), unit=unit)

    def getDesktopGutterClassName(self) -> str:
        gutterUnit = self.getDesktopUnit()
        gutter = self.getNormalizedGutterValue(gutterUnit)
        if gutterUnit == 'px':
            gutter = js_like_rounding(gutter)
        gutterUnitToken = 'per' if (gutterUnit == '%') else gutterUnit
        gutterToken = str(normalize_unit_value(gutter)).replace('.', '-')
        directionToken = '-rtl' if (self.context.get('direction') == 'rtl') else ''
        sibling = self.props['sibling']
        index = self.props['index']
        return (
            f'mj-column-gutter-{sibling}-{index + 1}'
            f'-{gutterUnitToken}-{gutterToken}{directionToken}'
        )

    def getDesktopPaddingValues(self, unit: str) -> Padding:
        first = self.props['first']
        last = self.props['last']
        sibling = self.props['sibling']
        if sibling == 1:
            return Padding(top=0, right=0, bottom=0, left=0)

        is_px = (unit == 'px')
        gutter = self.getNormalizedGutterValue(unit)
        if is_px:
            gutter = js_like_rounding(gutter)
            halfLeading = math.ceil(gutter / 2)
            halfTrailing = math.floor(gutter / 2)
        else:
            halfLeading = halfTrailing = gutter / 2

        if self.context.get('direction') == 'rtl':
            # when RTL, first/last visual positions are reversed
            return Padding(
                top=0,
                right=0 if first else halfTrailing,
                bottom=0,
                left=0 if last else halfLeading,
            )
        return Padding(
            top=0,
            right=0 if last else halfLeading,
            bottom=0,
            left=0 if first else halfTrailing,
        )

    def getMobilePaddingValues(self) -> Padding:
        # On mobile the gutter becomes vertical spacing between the stacked
        # columns but there is no spacing on the outer top/bottom edges.
        first = self.props['first']
        last = self.props['last']
        half = self.getNormalizedGutterValue('%') / 2
        return Padding(
            top=0 if first else half,
            right=0,
            bottom=0 if last else half,
            left=0,
        )

    @staticmethod
    def formatPadding(padding: Padding, unit: str) -> str:
        if unit == 'px':
            values = [f'{js_like_rounding(value)}px' for value in padding]
        else:
            values = [f'{normalize_unit_value(value)}{unit}' for value in padding]
        return ' '.join(values)

    def getDesktopPadding(self) -> str:
        unit = self.getDesktopUnit()
        return self.formatPadding(self.getDesktopPaddingValues(unit), unit)

    def getMobilePadding(self) -> str:
        return self.formatPadding(self.getMobilePaddingValues(), '%')

    def getMobileGutterStyles(self) -> dict:
        if not self.hasColumnGutter():
            return {}
        elif self.context.get('isInGroup'):
            # Group columns don't stack on mobile so they keep the horizontal
            # desktop padding.
            return {'padding': self.getDesktopPadding()}
        return {'padding': self.getMobilePadding()}

    def getOutlookGutterStyles(self) -> dict:
        if not self.hasColumnGutter():
            return {}
        return {'padding': self.formatPadding(self.getDesktopPaddingValues('px'), 'px')}

    def hasGutter(self):
        # upstream name - this is about the column's own padding, the section
        # "gutter" attribute is handled by ".hasColumnGutter()".
        padding_attrs = (
            'padding',
            'padding-bottom',
            'padding-left',
            'padding-right',
            'padding-top'
        )
        attr_values = map(lambda n: self.get_attr(n), padding_attrs)
        return any(filter(lambda v: bool(v), attr_values))

    def renderGutter(self):
        table_attrs = self.html_attrs(**{
            'border': '0',
            'cellpadding': '0',
            'cellspacing': '0',
            'role': 'presentation',
            'width': '100%',
        })
        return f'''<table {table_attrs}>
            <tbody>
              <tr>
                <td {self.html_attrs(style='gutter')}>
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
                align = component.getAttribute('align', missing_ok=True),
                class_ = component.getAttribute('css-class', missing_ok=True),
                style = {
                    'background': component.getAttribute(
                        'container-background-color',
                        missing_ok=True
                    ),
                    'font-size': '0px',
                    'padding': component.getAttribute('padding'),
                    'padding-top': component.getAttribute('padding-top'),
                    'padding-right': component.getAttribute('padding-right'),
                    'padding-bottom': component.getAttribute('padding-bottom'),
                    'padding-left': component.getAttribute('padding-left'),
                    'word-break': 'break-word',
                },
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
            <tbody>
                {self.renderChildren(children, renderer=render_child)}
            </tbody>
        </table>'''


def normalize_unit_value(value: Union[int, float, str]) -> Union[int, float]:
    # js: Number(parseFloat(value).toFixed(6))
    # Upstream rounds to six decimals, so a width renders as "48.333333%" and
    # not as "48.33333333333333%". Whole numbers are returned as int because
    # JS omits the trailing ".0".
    if isinstance(value, str):
        value = parse_float(value)
    rounded = float(f'{value:.6f}')
    return int(rounded) if (rounded == int(rounded)) else rounded


def js_like_rounding(value: Union[float, str]) -> int:
    # JS uses `Math.round()` which rounds half towards positive infinity.
    # Python's `round()` uses round half to even ("banker's rounding").
    if isinstance(value, str):
        value = parse_float(value)
    return math.floor(value + 0.5)
