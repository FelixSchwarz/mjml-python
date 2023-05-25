
from ._base import BodyComponent


__all__ = ['MjAccordion']

class MjAccordion(BodyComponent):
    component_name = 'mj-accordion'

    @classmethod
    def allowed_attrs(cls):
        return {
            'container-background-color': 'color',
            'border'                    : 'string',
            'font-family'               : 'string',
            'icon-align'                : 'enum(top,middle,bottom)',
            'icon-width'                : 'unit(px,%)',
            'icon-height'               : 'unit(px,%)',
            'icon-wrapped-url'          : 'string',
            'icon-wrapped-alt'          : 'string',
            'icon-unwrapped-url'        : 'string',
            'icon-unwrapped-alt'        : 'string',
            'icon-position'             : 'enum(left,right)',
            'padding-bottom'            : 'unit(px,%)',
            'padding-left'              : 'unit(px,%)',
            'padding-right'             : 'unit(px,%)',
            'padding-top'               : 'unit(px,%)',
            'padding'                   : 'unit(px,%){1,4}',
        }

    @classmethod
    def default_attrs(cls):
        return {
            'border'            : '2px solid black',
            'font-family'       : 'Ubuntu, Helvetica, Arial, sans-serif',
            'icon-align'        : 'middle',
            'icon-wrapped-url'  : 'https://i.imgur.com/bIXv1bk.png',
            'icon-wrapped-alt'  : '+',
            'icon-unwrapped-url': 'https://i.imgur.com/w4uTygT.png',
            'icon-unwrapped-alt': '-',
            'icon-position'     : 'right',
            'icon-height'       : '32px',
            'icon-width'        : '32px',
            'padding'           : '10px 25px',
        }

    def headStyle(self, breakpoint):
        return '''
            noinput.mj-accordion-checkbox { display:block!important; }
            @media yahoo, only screen and (min-width:0) {
                .mj-accordion-element { display:block; }
                input.mj-accordion-checkbox, .mj-accordion-less { display:none!important; }
                input.mj-accordion-checkbox + * .mj-accordion-title {
                    cursor:pointer;
                    touch-action:manipulation;
                    -webkit-user-select:none;
                    -moz-user-select:none;
                    user-select:none;
                }
                input.mj-accordion-checkbox + * .mj-accordion-content {
                    overflow:hidden;
                    display:none;
                }
                input.mj-accordion-checkbox + * .mj-accordion-more { display:block!important; }
                input.mj-accordion-checkbox:checked + * .mj-accordion-content { display:block; }
                input.mj-accordion-checkbox:checked + * .mj-accordion-more {
                    display:none!important;
                }
                input.mj-accordion-checkbox:checked + * .mj-accordion-less {
                    display:block!important;
                }
            }

            .moz-text-html input.mj-accordion-checkbox + * .mj-accordion-title {
                cursor: auto;
                touch-action: auto;
                -webkit-user-select: auto;
                -moz-user-select: auto;
                user-select: auto;
            }
            .moz-text-html input.mj-accordion-checkbox + * .mj-accordion-content {
                overflow: hidden;
                display: block;
            }
            .moz-text-html input.mj-accordion-checkbox + * .mj-accordion-ico { display: none; }

            @goodbye { @gmail }
        '''

    # js: getStyles()
    def get_styles(self):
        return {
            'table': {
                'width'          : '100%',
                'border-collapse': 'collapse',
                'border'         : self.get_attr('border'),
                'border-bottom'  : 'none',
                'font-family'    : self.get_attr('font-family'),
            },
        }

    def render(self):
        children = self.props['children']
        children_attrs = {
            'border'            : self.get_attr('border'),
            'icon-align'        : self.get_attr('icon-align'),
            'icon-width'        : self.get_attr('icon-width'),
            'icon-height'       : self.get_attr('icon-height'),
            'icon-position'     : self.get_attr('icon-position'),
            'icon-wrapped-url'  : self.get_attr('icon-wrapped-url'),
            'icon-wrapped-alt'  : self.get_attr('icon-wrapped-alt'),
            'icon-unwrapped-url': self.get_attr('icon-unwrapped-url'),
            'icon-unwrapped-alt': self.get_attr('icon-unwrapped-alt'),
        }
        table_attrs = self.html_attrs(
            cellspacing='0',
            cellpadding='0',
            class_='mj-accordion',
            style='table',
        )
        return f'''
            <table {table_attrs}>
                {self.renderChildren(children, attributes=children_attrs)}
            </table>
        '''
