
from ._base import BodyComponent


__all__ = ['MjText']

class MjText(BodyComponent):
    @classmethod
    def allowed_attrs(cls):
        return {
            'align'            : 'enum(left,right,center,justify)',
            'background-color' : 'color',
            'color'            : 'color',
            'container-background-color': 'color',
            'font-family'      : 'string',
            'font-size'        : 'unit(px)',
            'font-style'       : 'string',
            'font-weight'      : 'string',
            'height'           : 'unit(px,%)',
            'letter-spacing'   : 'unitWithNegative(px,%)',
            'line-height'      : 'unit(px,%,)',
            'padding-bottom'   : 'unit(px,%)',
            'padding-left'     : 'unit(px,%)',
            'padding-right'    : 'unit(px,%)',
            'padding-top'      : 'unit(px,%)',
            'padding'          : 'unit(px,%){1,4}',
            'text-decoration'  : 'string',
            'text-transform'   : 'string',
            'vertical-align'   : 'enum(top,bottom,middle)',
            # other attrs
            'css-class'        : '',
  }

    @classmethod
    def default_attrs(cls):
        return {
            'align'            : 'left',
            'color'            : '#000000',
            'font-family'      : 'Ubuntu, Helvetica, Arial, sans-serif',
            'font-size'        : '13px',
            'line-height'      : '1',
            'padding'          : '10px 25px',
        }

    def get_styles(self):
        style_attrs = {
            'font-family': self.get_attr('font-family'),
            'font-size': self.get_attr('font-size'),
            'font-style': self.get_attr('font-style'),
            'font-weight': self.get_attr('font-weight'),
            'letter-spacing': self.get_attr('letter-spacing'),
            'line-height': self.get_attr('line-height'),
            'text-align': self.get_attr('align'),
            'text-decoration': self.get_attr('text-decoration'),
            'text-transform': self.get_attr('text-transform'),
            'color': self.get_attr('color'),
            'height': self.get_attr('height'),
        }
        return {'text': style_attrs}

    def render(self):
        height = self.getAttribute('height')
        if not height:
            return self._render_content()

        start_conditional = f'''
            <table role="presentation" border="0" cellpadding="0" cellspacing="0"><tr><td height="{height}" style="vertical-align:top;height:{height};">
        '''
        end_conditional = '</td></tr></table>'
        return f'''{start_conditional}{self._render_content()}{end_conditional}'''

    def _render_content(self):
        content_html = self.getContent()
        return '<div ' + self.html_attrs(style='text') + '>' + content_html + '</div>'

