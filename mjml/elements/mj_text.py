
from ._base import BodyComponent


__all__ = ['MjText']

class MjText(BodyComponent):

    @classmethod
    def default_attrs(cls):
        return {
            'align'      : 'left',
            'color'      : '#000000',
            'font-family': 'Ubuntu, Helvetica, Arial, sans-serif',
            'font-size'  : '13px',
            'line-height': '1',
            'padding'    : '10px 25px',

            # other attrs
            'container-background-color': '',
            'font-style'       : '',
            'font-weight'      : '',
            'height'           : '',
            'letter-spacing'   : '',
            'padding-bottom'   : '',
            'padding-left'     : '',
            'padding-right'    : '',
            'padding-top'      : '',
            'text-decoration'  : '',
            'text-transform'   : '',
            'vertical-align'   : '',
            'css-class'        : '',
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
        return '<div ' + self.html_attrs(style='text') + '>' + self.getContent() + '</div>'

