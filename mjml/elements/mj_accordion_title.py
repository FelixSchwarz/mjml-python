
from ._base import BodyComponent


__all__ = ['MjAccordionTitle']

from ..helpers import conditionalTag


class MjAccordionTitle(BodyComponent):
    component_name = 'mj-accordion-title'

    @classmethod
    def allowed_attrs(cls):
        return {
            'background-color': 'color',
            'color'           : 'color',
            'font-size'       : 'unit(px)',
            'font-family'     : 'string',
            'padding-bottom'  : 'unit(px,%)',
            'padding-left'    : 'unit(px,%)',
            'padding-right'   : 'unit(px,%)',
            'padding-top'     : 'unit(px,%)',
            'padding'         : 'unit(px,%){1,4}',
        }

    @classmethod
    def default_attrs(cls):
        return {
            'font-size': '13px',
            'padding'  : '16px',
        }

    # js: getStyles()
    def get_styles(self):
        return {
            'td'   : {
                'width'           : '100%',
                'background-color': self.getAttribute('background-color'),
                'color'           : self.getAttribute('color'),
                'font-size'       : self.getAttribute('font-size'),
                'font-family'     : self.getAttribute('font-family'),
                'padding-bottom'  : self.getAttribute('padding-bottom'),
                'padding-left'    : self.getAttribute('padding-left'),
                'padding-right'   : self.getAttribute('padding-right'),
                'padding-top'     : self.getAttribute('padding-top'),
                'padding'         : self.getAttribute('padding'),
            },
            'table': {
                'width'        : '100%',
                'border-bottom': self.getAttribute('border', missing_ok=True),
            },
            'td2'  : {
                'padding'       : '16px',
                'background'    : self.getAttribute('background-color'),
                'vertical-align': self.getAttribute('icon-align', missing_ok=True),
            },
            'img'  : {
                'display': 'none',
                'width'  : self.getAttribute('icon-width', missing_ok=True),
                'height' : self.getAttribute('icon-height', missing_ok=True),
            },
        }

    def renderTitle(self):
        td_attrs = self.html_attrs(
            class_=self.getAttribute('css-class', missing_ok=True),
            style='td',
        )

        return f'''
            <td {td_attrs}>
                {self.getContent()}
            </td>
        '''

    def renderIcons(self):
        td_attrs = self.html_attrs(
            class_='mj-accordion-ico',
            style='td2',
        )
        img_more_attrs = self.html_attrs(
            src=self.getAttribute('icon-wrapped-url', missing_ok=True),
            alt=self.getAttribute('icon-wrapped-alt', missing_ok=True),
            class_='mj-accordion-more',
            style='img',
        )
        img_less_attrs = self.html_attrs(
            src=self.getAttribute('icon-unwrapped-url', missing_ok=True),
            alt=self.getAttribute('icon-unwrapped-alt', missing_ok=True),
            class_='mj-accordion-less',
            style='img',
        )

        return conditionalTag(
            f'''
            <td {td_attrs}>
                <img {img_more_attrs} />
                <img {img_less_attrs} />
            </td>
            ''',
            True
        )

    def render(self):
        content_elements = [self.renderTitle(), self.renderIcons()]
        if self.getAttribute('icon-position', missing_ok=True) != 'right':
            content_elements.reverse()
        content = '\n'.join(content_elements)

        div_attrs = self.html_attrs(
            class_='mj-accordion-title',
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
                            {content}
                        </tr>
                    </tbody>
                </table>
            </div>
        '''
