
from ._base import BodyComponent


__all__ = ['MjSocial']

class MjSocial(BodyComponent):
    component_name = 'mj-social'

    @classmethod
    def allowed_attrs(cls):
        return {
            'align'                     : 'enum(left,right,center)',
            'border-radius'             : 'unit(px,%)',
            'container-background-color': 'color',
            'color'                     : 'color',
            'font-family'               : 'string',
            'font-size'                 : 'unit(px)',
            'font-style'                : 'string',
            'font-weight'               : 'string',
            'icon-size'                 : 'unit(px,%)',
            'icon-height'               : 'unit(px,%)',
            'icon-padding'              : 'unit(px,%){1,4}',
            'inner-padding'             : 'unit(px,%){1,4}',
            'line-height'               : 'unit(px,%,)',
            'mode'                      : 'enum(horizontal,vertical)',
            'padding-bottom'            : 'unit(px,%)',
            'padding-left'              : 'unit(px,%)',
            'padding-right'             : 'unit(px,%)',
            'padding-top'               : 'unit(px,%)',
            'padding'                   : 'unit(px,%){1,4}',
            'table-layout'              : 'enum(auto,fixed)',
            'text-padding'              : 'unit(px,%){1,4}',
            'text-decoration'           : 'string',
            'vertical-align'            : 'enum(top,bottom,middle)',
        }

    @classmethod
    def default_attrs(cls):
        return {
            'align'          : 'center',
            'border-radius'  : '3px',
            'color'          : '#333333',
            'font-family'    : 'Ubuntu, Helvetica, Arial, sans-serif',
            'font-size'      : '13px',
            'icon-size'      : '20px',
            'inner-padding'  : None,
            'line-height'    : '22px',
            'mode'           : 'horizontal',
            'padding'        : '10px 25px',
            'text-decoration': 'none',
        }

    # js: getStyles()
    def get_styles(self):
        return {
            'tableVertical': {
                'margin': '0px',
            },
        }

    def getSocialElementAttributes(self):
        base = {}
        padding = self.getAttribute('inner-padding')
        if padding:
            base['padding'] = padding

        for attr_name in [
            'border-radius',
            'color',
            'font-family',
            'font-size',
            'font-weight',
            'font-style',
            'icon-size',
            'icon-height',
            'icon-padding',
            'text-padding',
            'line-height',
            'text-decoration',
        ]:
            attr = self.getAttribute(attr_name)
            if attr is not None:
                base[attr_name] = attr

        return base

    def renderHorizontal(self):
        children = self.props['children']
        align = self.getAttribute('align')

        def render_child(component):
            if component.isRawElement():
                return component.render()
            table_attrs = component.html_attrs(
                align=align,
                border='0',
                cellpadding='0',
                cellspacing='0',
                role='presentation',
                style={
                    'float'  : 'none',
                    'display': 'inline-table',
                },
            )
            return f'''
                <!--[if mso | IE]>
                    <td>
                <![endif]-->
                    <table {table_attrs}>
                        <tbody>
                            {component.render()}
                        </tbody>
                    </table>
                <!--[if mso | IE]>
                    </td>
                <![endif]-->
            '''

        table_attrs = self.html_attrs(
            align       = align,
            border      = '0',
            cellpadding = '0',
            cellspacing = '0',
            role        = 'presentation',
        )
        return f'''
            <!--[if mso | IE]>
                <table {table_attrs}>
                    <tr>
            <![endif]-->
            {self.renderChildren(children, attributes=self.getSocialElementAttributes(), renderer=render_child)}
            <!--[if mso | IE]>
                    </tr>
                </table>
            <![endif]-->
        ''' # noqa: E501

    def renderVertical(self):
        table_attrs = self.html_attrs(
            border      = '0',
            cellpadding = '0',
            cellspacing = '0',
            role        = 'presentation',
            style       = 'tableVertical',
        )
        children = self.props['children']
        return f'''
            <table {table_attrs}>
                <tbody>
                    {self.renderChildren(children, attributes=self.getSocialElementAttributes())}
                </tbody>
            </table>
        '''

    def render(self):
        if self.getAttribute('mode') == 'horizontal':
            return self.renderHorizontal()
        return self.renderVertical()
