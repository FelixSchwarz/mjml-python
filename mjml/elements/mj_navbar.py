
from secrets import token_hex

from ._base import BodyComponent
from ..helpers import msoConditionalTag, conditionalTag


__all__ = ['MjNavbar']


class MjNavbar(BodyComponent):
    @classmethod
    def allowed_attrs(cls):
        return {
            'align'              : 'enum(left,center,right)',
            'base-url'           : 'string',
            'hamburger'          : 'string',
            'ico-align'          : 'enum(left,center,right)',
            'ico-open'           : 'string',
            'ico-close'          : 'string',
            'ico-color'          : 'color',
            'ico-font-size'      : 'unit(px,%)',
            'ico-font-family'    : 'string',
            'ico-text-transform' : 'string',
            'ico-padding'        : 'unit(px,%){1,4}',
            'ico-padding-left'   : 'unit(px,%)',
            'ico-padding-top'    : 'unit(px,%)',
            'ico-padding-right'  : 'unit(px,%)',
            'ico-padding-bottom' : 'unit(px,%)',
            'padding'            : 'unit(px,%){1,4}',
            'padding-left'       : 'unit(px,%)',
            'padding-top'        : 'unit(px,%)',
            'padding-right'      : 'unit(px,%)',
            'padding-bottom'     : 'unit(px,%)',
            'ico-text-decoration': 'string',
            'ico-line-height'    : 'unit(px,%,)',
        }

    @classmethod
    def default_attrs(cls):
        return {
            'align'              : 'center',
            'base-url'           : None,
            'hamburger'          : None,
            'ico-align'          : 'center',
            'ico-open'           : '&#9776;',
            'ico-close'          : '&#8855;',
            'ico-color'          : '#000000',
            'ico-font-size'      : '30px',
            'ico-font-family'    : 'Ubuntu, Helvetica, Arial, sans-serif',
            'ico-text-transform' : 'uppercase',
            'ico-padding'        : '10px',
            'ico-text-decoration': 'none',
            'ico-line-height'    : '30px',
        }

    def headStyle(self, breakpoint):
        # double curly braces used to escape "{" and "}" in f-strings
        return f'''
            noinput.mj-menu-checkbox {{ display:block!important; max-height:none!important; visibility:visible!important; }}
            @media only screen and (max-width:{breakpoint}) {{
              .mj-menu-checkbox[type="checkbox"] ~ .mj-inline-links {{ display:none!important; }}
              .mj-menu-checkbox[type="checkbox"]:checked ~ .mj-inline-links,
              .mj-menu-checkbox[type="checkbox"] ~ .mj-menu-trigger {{ display:block!important; max-width:none!important; max-height:none!important; font-size:inherit!important; }}
              .mj-menu-checkbox[type="checkbox"] ~ .mj-inline-links > a {{ display:block!important; }}
              .mj-menu-checkbox[type="checkbox"]:checked ~ .mj-menu-trigger .mj-menu-icon-close {{ display:block!important; }}
              .mj-menu-checkbox[type="checkbox"]:checked ~ .mj-menu-trigger .mj-menu-icon-open {{ display:none!important; }}
            }}'''

    def get_styles(self):
        return {
            'div': {
                'align': self.getAttribute('align'),
                'width': '100%',
            },
            'label': {
                'display'         : 'block',
                'cursor'          : 'pointer',
                'mso-hide'        : 'all',
                '-moz-user-select': 'none',
                'user-select'     : 'none',
                'color'           : self.getAttribute('ico-color'),
                'font-size'       : self.getAttribute('ico-font-size'),
                'font-family'     : self.getAttribute('ico-font-family'),
                'text-transform'  : self.getAttribute('ico-text-transform'),
                'text-decoration' : self.getAttribute('ico-text-decoration'),
                'line-height'     : self.getAttribute('ico-line-height'),
                'padding-top'     : self.getAttribute('ico-padding-top'),
                'padding-right'   : self.getAttribute('ico-padding-right'),
                'padding-bottom'  : self.getAttribute('ico-padding-bottom'),
                'padding-left'    : self.getAttribute('ico-padding-left'),
                'padding'         : self.getAttribute('ico-padding'),
            },
            'trigger': {
                'display'   : 'none',
                'max-height': '0px',
                'max-width' : '0px',
                'font-size' : '0px',
                'overflow'  : 'hidden',
            },
            'icoOpen': {
                'mso-hide': 'all',
            },
            'icoClose': {
                'display' : 'none',
                'mso-hide': 'all',
            },
        }

    def renderHamburger(self):
        key = token_hex(8)

        return f'''
          {msoConditionalTag(
            f'<input type="checkbox" id="{key}" class="mj-menu-checkbox" style="display:none !important; max-height:0; visibility:hidden;" />',
            True
          )}
          <div
            {self.html_attrs(
                class_='mj-menu-trigger',
                style='trigger',
            )}
          >
            <label
              {self.html_attrs(
                for_=key,
                class_='mj-menu-label',
                style='label',
                align=self.getAttribute('ico-align'),
              )}
            >
              <span
                {self.html_attrs(
                  class_='mj-menu-icon-open',
                  style='icoOpen',
                )}
              >
                {self.getAttribute('ico-open')}
              </span>
              <span
                {self.html_attrs(
                  class_='mj-menu-icon-close',
                  style='icoClose',
                )}
              >
                {self.getAttribute('ico-close')}
              </span>
            </label>
          </div>
        '''

    def render(self):
        children = self.props['children']
        hamburger = self.renderHamburger() if self.getAttribute('hamburger') == 'hamburger' else ''
        conditional_open, conditional_close = [
            conditionalTag(f'''
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" align="{self.getAttribute('align')}">
              <tr>
            '''),
            conditionalTag('</tr></table>')
        ]
        div_attrs = self.html_attrs(
            class_='mj-inline-links',
        )

        return f'''
            {hamburger}
            <div {div_attrs}>
              {conditional_open}
              {self.renderChildren(children, 
                attributes={
                  'navbarBaseUrl': self.getAttribute('base-url'),
                },
              )}
              {conditional_close}
            </div>
        '''
