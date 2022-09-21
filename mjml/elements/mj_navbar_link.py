
from ._base import BodyComponent
from ..helpers import conditionalTag, suffixCssClasses


__all__ = ['MjNavbarLink']


class MjNavbarLink(BodyComponent):
    @classmethod
    def allowed_attrs(cls):
        return {
            'color'          : 'color',
            'font-family'    : 'string',
            'font-size'      : 'unit(px)',
            'font-style'     : 'string',
            'font-weight'    : 'string',
            'href'           : 'string',
            'name'           : 'string',
            'target'         : 'string',
            'rel'            : 'string',
            'letter-spacing' : 'unitWithNegative(px,em)',
            'line-height'    : 'unit(px,%,)',
            'padding-bottom' : 'unit(px,%)',
            'padding-left'   : 'unit(px,%)',
            'padding-right'  : 'unit(px,%)',
            'padding-top'    : 'unit(px,%)',
            'padding'        : 'unit(px,%){1,4}',
            'text-decoration': 'string',
            'text-transform' : 'string',
        }

    @classmethod
    def default_attrs(cls):
        return {
            'color'          : '#000000',
            'font-family'    : 'Ubuntu, Helvetica, Arial, sans-serif',
            'font-size'      : '13px',
            'font-weight'    : 'normal',
            'line-height'    : '22px',
            'padding'        : '15px 10px',
            'target'         : '_blank',
            'text-decoration': 'none',
            'text-transform' : 'uppercase',
        }

    def get_styles(self):
        return {
            'a': {
                'display'        : 'inline-block',
                'color'          : self.getAttribute('color'),
                'font-family'    : self.getAttribute('font-family'),
                'font-size'      : self.getAttribute('font-size'),
                'font-style'     : self.getAttribute('font-style'),
                'font-weight'    : self.getAttribute('font-weight'),
                'letter-spacing' : self.getAttribute('letter-spacing'),
                'line-height'    : self.getAttribute('line-height'),
                'text-decoration': self.getAttribute('text-decoration'),
                'text-transform' : self.getAttribute('text-transform'),
                'padding'        : self.getAttribute('padding'),
                'padding-top'    : self.getAttribute('padding-top'),
                'padding-left'   : self.getAttribute('padding-left'),
                'padding-right'  : self.getAttribute('padding-right'),
                'padding-bottom' : self.getAttribute('padding-bottom'),
            },
            'td': {
                'padding'       : self.getAttribute('padding'),
                'padding-top'   : self.getAttribute('padding-top'),
                'padding-left'  : self.getAttribute('padding-left'),
                'padding-right' : self.getAttribute('padding-right'),
                'padding-bottom': self.getAttribute('padding-bottom'),
            },
        }

    def renderContent(self):
        href = self.getAttribute('href')
        navbarBaseUrl = self.getAttribute('navbarBaseUrl')
        link = f'{navbarBaseUrl}{href}' if navbarBaseUrl else href

        cssClass = f' {self.getAttribute("css-class")}' if self.getAttribute('css-class') else ''

        return f'''
          <a
            {self.html_attrs(
              class_=f'mj-link{cssClass}',
              href=link,
              rel=self.getAttribute('rel'),
              target=self.getAttribute('target'),
              name=self.getAttribute('name'),
              style='a',
            )}
          >
            {self.getContent()}
          </a>
        '''

    def render(self):
        conditional_open, conditional_close = [
            conditionalTag(f'''
            <td
                {self.html_attrs(
                  style='td',
                  class_=suffixCssClasses(
                    self.getAttribute('css-class'),
                    'outlook',
                  ),
                )}
              >
            '''),
            conditionalTag('</td>')
        ]

        return f'''
            {conditional_open}
            {self.renderContent()}
            {conditional_close}
        '''
