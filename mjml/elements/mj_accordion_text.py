
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
                'background'    : self.getAttribute('background-color'),
                'font-size'     : self.getAttribute('font-size'),
                'font-family'   : self.getAttribute('font-family'),
                'font-weight'   : self.getAttribute('font-weight'),
                'letter-spacing': self.getAttribute('letter-spacing'),
                'line-height'   : self.getAttribute('line-height'),
                'color'         : self.getAttribute('color'),
                'padding-bottom': self.getAttribute('padding-bottom'),
                'padding-left'  : self.getAttribute('padding-left'),
                'padding-right' : self.getAttribute('padding-right'),
                'padding-top'   : self.getAttribute('padding-top'),
                'padding'       : self.getAttribute('padding'),
            },
            'table': {
                'width'        : '100%',
                'border-bottom': self.getAttribute('border', missing_ok=True),
            },
        }

    def renderContent(self):
        td_attrs = self.html_attrs(
            class_=self.getAttribute('css-class', missing_ok=True),
            style='td',
        )

        return f'''
            <td {td_attrs}>
                {self.getContent()}
            </td>
        '''

    def render(self):
        div_attrs = self.html_attrs(
            class_='mj-accordion-content',
        )
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

