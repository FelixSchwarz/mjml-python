
from ._base import BodyComponent


__all__ = ['MjAccordionText']


class MjAccordionText(BodyComponent):
    component_name = 'mj-accordion-text'

    @classmethod
    def allowed_attrs(cls):
        return {
            'background-color': 'color',
            'font-size'       : 'unit(px)',
            'font-family'     : 'string',
            'font-weight'     : 'string',
            'letter-spacing'  : 'unitWithNegative(px,em)',
            'line-height'     : 'unit(px,%,)',
            'color'           : 'color',
            'padding-bottom'  : 'unit(px,%)',
            'padding-left'    : 'unit(px,%)',
            'padding-right'   : 'unit(px,%)',
            'padding-top'     : 'unit(px,%)',
            'padding'         : 'unit(px,%){1,4}',
        }

    @classmethod
    def default_attrs(cls):
        return {
            'font-size'  : '13px',
            'line-height': '1',
            'padding'    : '16px',
        }

    # js: getStyles()
    def get_styles(self):
        return {
            'td'   : {
                'background'    : self.get_attr('background-color'),
                'font-size'     : self.get_attr('font-size'),
                'font-family'   : self.get_attr('font-family'),
                'font-weight'   : self.get_attr('font-weight'),
                'letter-spacing': self.get_attr('letter-spacing'),
                'line-height'   : self.get_attr('line-height'),
                'color'         : self.get_attr('color'),
                'padding-bottom': self.get_attr('padding-bottom'),
                'padding-left'  : self.get_attr('padding-left'),
                'padding-right' : self.get_attr('padding-right'),
                'padding-top'   : self.get_attr('padding-top'),
                'padding'       : self.get_attr('padding'),
            },
            'table': {
                'width'        : '100%',
                'border-bottom': self.get_attr('border', missing_ok=True),
            },
        }

    def renderContent(self):
        td_attrs = self.html_attrs(
            class_=self.get_attr('css-class', missing_ok=True),
            style='td',
        )
        return f'''
            <td {td_attrs}>
                {self.getContent()}
            </td>
        '''

    def render(self):
        div_attrs = self.html_attrs(class_='mj-accordion-content')
        table_attrs = self.html_attrs(
            cellspacing='0',
            cellpadding='0',
            style='table',
        )
        return f'''
            <div {div_attrs}>
                <table {table_attrs}>
                    <tbody>
                        <tr>
                            {self.renderContent()}
                        </tr>
                    </tbody>
                </table>
            </div>
        '''
