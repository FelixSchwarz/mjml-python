

from ._base import BodyComponent
from ..helpers import suffixCssClasses, strip_unit
from ..lib import merge_dicts


class MjSection(BodyComponent):
    @classmethod
    def default_attrs(cls):
        return {
            'background-repeat': 'repeat',
            'background-size'  : 'auto',
            'direction'        : 'ltr',
            'padding'          : '20px 0',
            'text-align'       : 'center',
            'text-padding'     : '4px 4px 4px 0',

            # other attrs
            'background-color' : '',
            'background-url'   : '',
            'full-width'       : '',
            'border'           : '',
            'border-bottom'    : '',
            'border-left'      : '',
            'border-radius'    : '',
            'border-right'     : '',
            'border-top'       : '',
            'padding-top'      : '',
            'padding-bottom'   : '',
            'padding-left'     : '',
            'padding-right'    : '',
            'css-class'        : '',
        }

    def get_styles(self):
        containerWidth = self.context['containerWidth']
        fullWidth = self.isFullWidth()
        if self.getAttribute('background-url'):
            background = {'background': self.getBackground() }
        else:
            background = {
                'background': self.getAttribute('background-color'),
                'background-color': self.getAttribute('background-color'),
            }
        this = self
        return {
            'tableFullwidth': merge_dicts({
                'width': '100%',
                'border-radius': this.getAttribute('border-radius'),
                }, (background if fullWidth else {})
            ),
            'table': merge_dicts({
                'width': '100%',
                'border-radius': this.getAttribute('border-radius'),
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
                'border-radius': this.getAttribute('border-radius'),
                'max-width': containerWidth,
            }),
            'innerDiv': {
                'line-height': '0',
                'font-size': '0',
            },
        }

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

