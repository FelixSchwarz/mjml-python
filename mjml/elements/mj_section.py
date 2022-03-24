
from collections import namedtuple
from decimal import Decimal
import re

from ._base import BodyComponent
from ..helpers import parse_percentage, strip_unit, suffixCssClasses
from ..lib import merge_dicts, AttrDict


__all__ = ['MjSection']

Position = namedtuple('Position', ('x', 'y'))


class MjSection(BodyComponent):
    @classmethod
    def allowed_attrs(cls):
        return {
            'background-color' : 'color',
            'background-url'   : 'string',
            'background-repeat': 'enum(repeat,no-repeat)',
            'background-size'  : 'string',
            'background-position'  : 'string',
            'background-position-x': 'string',
            'background-position-y': 'string',
            'border'           : 'string',
            'border-bottom'    : 'string',
            'border-left'      : 'string',
            'border-radius'    : 'string',
            'border-right'     : 'string',
            'border-top'       : 'string',
            'direction'        : 'enum(ltr,rtl)',
            'full-width'       : 'enum(full-width)',
            'padding'          : 'unit(px,%){1,4}',
            'padding-top'      : 'unit(px,%)',
            'padding-bottom'   : 'unit(px,%)',
            'padding-left'     : 'unit(px,%)',
            'padding-right'    : 'unit(px,%)',
            'text-align'       : 'enum(left,center,right)',
            'text-padding'     : 'unit(px,%){1,4}',
        }

    @classmethod
    def default_attrs(cls):
        return {
            'background-repeat': 'repeat',
            'background-size'  : 'auto',
            'background-position': 'top center',
            'direction'        : 'ltr',
            'padding'          : '20px 0',
            'text-align'       : 'center',
            'text-padding'     : '4px 4px 4px 0',

            # other attrs
            'css-class'        : '',
        }

    def get_styles(self):
        containerWidth = self.context['containerWidth']
        fullWidth = self.isFullWidth()
        if self.hasBackground():
            background = {
                'background': self.getBackground(),
                # background size, repeat and position has to be separate since
                # yahoo does not support shorthand background css property
                'background-position': self.getBackgroundString(),
                'background-repeat': self.getAttribute('background-repeat'),
                'background-size': self.getAttribute('background-size'),
            }
        else:
            bg_color = self.getAttribute('background-color')
            background = {
                'background': bg_color,
                'background-color': bg_color,
            }
        this = self
        border_radius = self.getAttribute('border-radius')
        return {
            'tableFullwidth': merge_dicts({
                'width': '100%',
                'border-radius': border_radius,
                }, (background if fullWidth else {})
            ),
            'table': merge_dicts({
                'width': '100%',
                'border-radius': border_radius,
                }, ({} if fullWidth else background)
            ),
            'td': {
                'border': this.getAttribute('border'),
                'border-bottom': this.getAttribute('border-bottom'),
                'border-left': this.getAttribute('border-left'),
                'border-right': this.getAttribute('border-right'),
                'border-top': this.getAttribute('border-top'),
                'direction': this.getAttribute('direction'),
                'font-size': '0px',
                'padding': this.getAttribute('padding'),
                'padding-bottom': this.getAttribute('padding-bottom'),
                'padding-left': this.getAttribute('padding-left'),
                'padding-right': this.getAttribute('padding-right'),
                'padding-top': this.getAttribute('padding-top'),
                'text-align': this.getAttribute('text-align'),
            },
            'div': merge_dicts({} if fullWidth else background, {
                'margin': '0px auto',
                'border-radius': border_radius,
                'max-width': containerWidth,
            }),
            'innerDiv': {
                'line-height': '0',
                'font-size': '0',
            },
        }

    def getBackground(self):
        if self.hasBackground():
            bg_url = self.getAttribute('background-url')
            bg_size = self.getAttribute('background-size')
            bg_parts = [
                f"url('{bg_url}')",
                self.getBackgroundString(),
                f'/ {bg_size}',
                self.getAttribute('background-repeat'),
            ]
        else:
            bg_parts = []
        return makeBackgroundString([
            self.getAttribute('background-color'),
            *bg_parts,
        ])

    def getBackgroundString(self):
        bg_pos = self.getBackgroundPosition()
        return f'{bg_pos.posX} {bg_pos.posY}'

    def getChildContext(self):
        box = self.getBoxWidths()['box']
        child_context = merge_dicts(self.context, {'containerWidth': f'{box}px'})
        return child_context

    def render(self):
        if self.isFullWidth():
            return self.renderFullWidth()
        return self.renderSimple()

    def renderFullWidth(self):
        raise NotImplementedError()

    def renderSimple(self):
        section = self.renderSection()
        if self.hasBackground():
            section = self.renderWithBackground(section)

        return ''.join([
            self.renderBefore(),
            section,
            self.renderAfter()
        ])

    def getBackgroundPosition(self):
        pos = self.parseBackgroundPosition()
        return AttrDict({
            'posX': self.getAttribute('background-position-x') or pos.x,
            'posY': self.getAttribute('background-position-y') or pos.y,
        })

    def parseBackgroundPosition(self):
        posSplit = self.getAttribute('background-position').split(' ')
        if len(posSplit) == 1:
            val, = posSplit
            # here we must determine if x or y was provided; other will be center
            if val in ('top', 'bottom'):
                return Position(x='center', y=val)
            else:
                return Position(x=val, y='center')
        elif len(posSplit) == 2:
            # x and y can be put in any order in background-position so we need
            # to determine that based on values
            val1, val2 = posSplit
            val1_is_top_bottom = (val1 in ('top', 'bottom'))
            val2_is_left_right = (val2 in ('left', 'right'))
            if val1_is_top_bottom or (val1 == 'center' and val2_is_left_right):
                return Position(x=val2, y=val1)
            else:
                return Position(x=val1, y=val2)
        else:
            # more than 2 values is not supported, let's treat as default value
            return Position(x='center', y='top')

    def hasBackground(self):
        return bool(self.get_attr('background-url'))

    def isFullWidth(self):
        return self.get_attr('full-width') == 'full-width'

    def renderSection(self):
        hasBackground = self.hasBackground()

        wrapper_class = self.get_attr('css-class') if self.isFullWidth() else None
        wrapper_attr_str = self.html_attrs(class_=wrapper_class, style='div')

        bg_div_start = f'<div {self.html_attrs(style="innerDiv")}>' if hasBackground else ''
        bg_div_end = f'</div>' if hasBackground else ''

        table_attrs = self.html_attrs(
            align='center',
            background=None if self.isFullWidth() else self.get_attr('background-url'),
            border='0',
            cellpadding='0',
            cellspacing='0',
            role='presentation',
            style='table',
        )
        return f'''<div {wrapper_attr_str}>
        { bg_div_start }
        <table
          {table_attrs}
        >
          <tbody>
            <tr>
              <td
                {self.html_attrs(style='td')}
              >
                <!--[if mso | IE]>
                  <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                <![endif]-->
                  {self.renderWrappedChildren()}
                <!--[if mso | IE]>
                  </table>
                <![endif]-->
              </td>
            </tr>
          </tbody>
        </table>
        {bg_div_end}
      </div>'''


    def renderWrappedChildren(self):
        children = self.props['children']

        def render_child(component):
            if component.isRawElement():
                return component.render()
            td_ie_attrs = component.html_attrs(
                # TODO: no component has an "align" attr, also never used?
                #align=component.get_attr('align'),
                class_=suffixCssClasses(
                      component.get_attr('css-class'),
                      'outlook',
                    ),
                style='tdOutlook',
            )
            return f'''
              <!--[if mso | IE]>
                <td
                  {td_ie_attrs}
                >
              <![endif]-->
                {component.render()}
              <!--[if mso | IE]>
                </td>
              <![endif]-->
            '''

        return f'''
            <!--[if mso | IE]>
              <tr>
            <![endif]-->
            {self.renderChildren(children, renderer=render_child)}
            <!--[if mso | IE]>
              </tr>
            <![endif]-->'''

    def renderWithBackground(self, content):
        fullWidth = self.isFullWidth()
        containerWidth = self.context['containerWidth']

        vSizeAttributes = {}
        background_size = self.get_attr('background-size')
        # If background size is either cover or contain, we tell VML to keep
        # the aspect and fill the entire element.
        if background_size in ('cover', 'contain'):
            is_cover = (background_size == 'cover')
            vSizeAttributes = {
                'size'  : '1,1',
                'aspect': 'atleast' if is_cover else 'atmost',
            }
        elif background_size != 'auto':
            bgSplit = background_size.split(' ')
            if len(bgSplit) == 1:
                vSizeAttributes = {
                    'size'  : background_size,
                    'aspect': 'atmost', # reproduces height auto
                }
            else:
                vSizeAttributes = {
                  'size': ','.join(bgSplit),
                }

        is_bg_norepeat = (self.get_attr('background-repeat') == 'no-repeat')
        vmlType = 'frame' if is_bg_norepeat else 'tile'
        if background_size == 'auto':
            # if no size provided, keep old behavior because outlook can't use
            # original image size with "frame"
            vmlType = 'tile'
            # also ensure that images are still cropped the same way
            vX = 0.5
            vY = 0
        else:
            bgPos = self.getBackgroundPosition()
            bgPosX = self._get_bg_percentage(bgPos.posX, ('left', 'center', 'right'), default='50%')
            bgPosY = self._get_bg_percentage(bgPos.posY, ('top', 'center', 'bottom'), default='0%')
            # this logic is different when using repeat or no-repeat
            vX = self._calc_origin_pos_value(is_x=True, bg_pos=bgPosX)
            vY = self._calc_origin_pos_value(is_y=False, bg_pos=bgPosY)

        vrect_style = {'mso-width-percent': '1000'} if fullWidth else {'width': str(containerWidth)}
        vrect_attrs = self.html_attrs(**{
            'style'  : vrect_style,
            'xmlns:v': 'urn:schemas-microsoft-com:vml',
            'fill'   : 'true',
            'stroke' : 'false',
        })
        vfill_attrs = self.html_attrs(**{
            'origin': f'{vX}, {vY}',
            'position': f'{vX}, {vY}',
            'src': self.getAttribute('background-url'),
            'color': self.getAttribute('background-color'),
            'type': vmlType,
            **vSizeAttributes,
        })
        return f'''
          <!--[if mso | IE]>
            <v:rect {vrect_attrs} />
            <v:textbox style="mso-fit-shape-to-text:true" inset="0,0,0,0">
            <v:fill {vfill_attrs} />
          <![endif]-->
              {content}
            <!--[if mso | IE]>
            </v:textbox>
          </v:rect>
        <![endif]-->
        '''

    def _get_bg_percentage(self, pos_value, fixed_keys, *, default):
        assert len(fixed_keys) == 3
        attr_map = dict(zip(fixed_keys, ('0%', '50%', '100%')))
        if pos_value in attr_map:
            return attr_map[pos_value]
        elif is_percentage(pos_value):
            return pos_value
        return default

    def _calc_origin_pos_value(self, is_x, bg_pos):
        bgRepeat = (self.getAttribute('background-repeat') == 'repeat')
        value = bg_pos
        if is_percentage(value):
            # Should be percentage at this point
            percentage_value = parse_percentage(value)
            decimal = int(percentage_value) / Decimal(100)
            if bgRepeat:
                value = decimal
            else:
                value = (-50 + decimal * 100) / 100
        elif bgRepeat:
            # top (y) or center (x)
            value = '0.5' if is_x else '0'
        else:
            value = '0' if is_x else '-0.5'
        return value

    def renderBefore(self):
        containerWidth = self.context['containerWidth']
        containerWidth_int = strip_unit(containerWidth)
        table_attrs = self.html_attrs(
          align = 'center',
          border = '0',
          cellpadding = '0',
          cellspacing = '0',
          class_ = suffixCssClasses(self.get_attr('css-class'), 'outlook'),
          style = {'width': str(containerWidth)},
          width = containerWidth_int,
        )
        return f'''
            <!--[if mso | IE]>
            <table
              {table_attrs}
            >
              <tr>
                <td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;">
            <![endif]-->
        '''

    def renderAfter(self):
        return '''
            <!--[if mso | IE]>
                </td>
              </tr>
            </table>
            <![endif]-->'''


def is_percentage(value):
    match = re.search(r'^\d+(\.\d+)?%$', value)
    return (match is not None)

def makeBackgroundString(parts):
    return ' '.join(filter(None, parts))

