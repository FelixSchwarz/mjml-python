
from ..helpers import parse_int, widthParser
from ..lib import merge_dicts
from ._base import BodyComponent


__all__ = ['MjHero']


class MjHero(BodyComponent):
    component_name = 'mj-hero'

    @classmethod
    def allowed_attrs(cls):
        return {
            'mode'                      : 'string',
            'height'                    : 'unit(px,%)',
            'background-url'            : 'string',
            'background-width'          : 'unit(px,%)',
            'background-height'         : 'unit(px,%)',
            'background-position'       : 'string',
            'border-radius'             : 'string',
            'container-background-color': 'color',
            'inner-background-color'    : 'color',
            'inner-padding'             : 'unit(px,%){1,4}',
            'inner-padding-top'         : 'unit(px,%)',
            'inner-padding-left'        : 'unit(px,%)',
            'inner-padding-right'       : 'unit(px,%)',
            'inner-padding-bottom'      : 'unit(px,%)',
            'padding'                   : 'unit(px,%){1,4}',
            'padding-bottom'            : 'unit(px,%)',
            'padding-left'              : 'unit(px,%)',
            'padding-right'             : 'unit(px,%)',
            'padding-top'               : 'unit(px,%)',
            'background-color'          : 'color',
            'vertical-align'            : 'enum(top,bottom,middle)',
        }

    @classmethod
    def default_attrs(cls):
        return {
            'mode'               : 'fixed-height',
            'height'             : '0px',
            'background-url'     : None,
            'background-position': 'center center',
            'padding'            : '0px',
            'padding-bottom'     : None,
            'padding-left'       : None,
            'padding-right'      : None,
            'padding-top'        : None,
            'background-color'   : '#ffffff',
            'vertical-align'     : 'top',
        }

    def getChildContext(self):
        containerWidth = self.context['containerWidth']
        padding_left = self.getShorthandAttrValue('padding', 'left')
        padding_right = self.getShorthandAttrValue('padding', 'right')
        paddingSize = padding_left + padding_right

        container_width: int = parse_int(containerWidth)
        parsed_width, unit = widthParser(f'{container_width}px', parseFloatToInt=False)
        if unit == '%':
            container_width = (container_width * parsed_width) / 100 - paddingSize
        else:
            container_width = parsed_width - paddingSize
        currentContainerWidth = f'{container_width}px'

        return merge_dicts(
            self.context,
            {'containerWidth': currentContainerWidth}
        )


    # js: getStyles()
    def get_styles(self):
        containerWidth = self.context['containerWidth']
        backgroundHeight = self.get_attr('background-height')
        backgroundWidth = self.get_attr('background-width')
        backgroundRatio = round(
            (parse_int(backgroundHeight) /
             parse_int(backgroundWidth)) *
            100
        )
        width = backgroundWidth or containerWidth

        return {
            'div'                : {
                'margin'   : '0 auto',
                'max-width': containerWidth,
            },
            'table'              : {
                'width': '100%',
            },
            'tr'                 : {
                'vertical-align': 'top',
            },
            'td-fluid'           : {
                'width'                 : '0.01%',
                'padding-bottom'        : f'{backgroundRatio}%',
                'mso-padding-bottom-alt': '0',
            },
            'hero'               : {
                'background'         : self.getBackground(),
                'background-position': self.get_attr('background-position'),
                'background-repeat'  : 'no-repeat',
                'border-radius'      : self.get_attr('border-radius'),
                'padding'            : self.get_attr('padding'),
                'padding-top'        : self.get_attr('padding-top'),
                'padding-left'       : self.get_attr('padding-left'),
                'padding-right'      : self.get_attr('padding-right'),
                'padding-bottom'     : self.get_attr('padding-bottom'),
                'vertical-align'     : self.get_attr('vertical-align'),
            },
            'outlook-table'      : {
                'width': containerWidth,
            },
            'outlook-td'         : {
                'line-height'         : 0,
                'font-size'           : 0,
                'mso-line-height-rule': 'exactly',
            },
            'outlook-inner-table': {
                'width': containerWidth,
            },
            'outlook-image'      : {
                'border'                 : '0',
                'height'                 : backgroundHeight,
                'mso-position-horizontal': 'center',
                'position'               : 'absolute',
                'top'                    : 0,
                'width'                  : width,
                'z-index'                : '-3',
            },
            'outlook-inner-td'   : {
                'background-color': self.get_attr('inner-background-color'),
                'padding'         : self.get_attr('inner-padding'),
                'padding-top'     : self.get_attr('inner-padding-top'),
                'padding-left'    : self.get_attr('inner-padding-left'),
                'padding-right'   : self.get_attr('inner-padding-right'),
                'padding-bottom'  : self.get_attr('inner-padding-bottom'),
            },
            'inner-table'        : {
                'width' : '100%',
                'margin': '0px',
            },
            'inner-div'          : {
                'background-color': self.get_attr('inner-background-color'),
                'float'           : self.get_attr('align', missing_ok=True),
                'margin'          : '0px auto',
                'width'           : self.get_attr('width', missing_ok=True),
            },
        }

    def hasBackground(self):
        return bool(self.get_attr('background-url'))

    def getBackground(self):
        if self.hasBackground():
            bg_url = self.getAttribute('background-url')
            bg_position = self.getAttribute('background-position')
            bg_parts = [
                f"url('{bg_url}')",
                'no-repeat',
                f'{bg_position} / cover',
            ]
        else:
            bg_parts = []

        return makeBackgroundString([
            self.getAttribute('background-color'),
            *bg_parts,
        ])

    def renderContent(self):
        containerWidth = self.context['containerWidth']
        children = self.props['children']

        def render_child(component):
            if component.isRawElement():
                return component.render()
            td_attrs = component.html_attrs(
                align=component.getAttribute('align', missing_ok=True),
                background=component.getAttribute('container-background-color'),
                class_=component.getAttribute('css-class'),
                style={
                    'background'    : component.getAttribute('container-background-color'),
                    'font-size'     : '0px',
                    'padding'       : component.getAttribute('padding'),
                    'padding-top'   : component.getAttribute('padding-top'),
                    'padding-right' : component.getAttribute('padding-right'),
                    'padding-bottom': component.getAttribute('padding-bottom'),
                    'padding-left'  : component.getAttribute('padding-left'),
                    'word-break'    : 'break-word',
                },
            )
            return f'''
                <tr>
                    <td {td_attrs}>
                        {component.render()}
                    </td>
                </tr>
            '''

        mso_table_attrs = self.html_attrs(
            align=self.getAttribute('align', missing_ok=True),
            border='0',
            cellpadding='0',
            cellspacing='0',
            style='outlook-inner-table',
            width=containerWidth.replace('px', ''),
        )
        div_attrs = self.html_attrs(
            align=self.getAttribute('align', missing_ok=True),
            class_='mj-hero-content',
            style='inner-div',
        )
        inner_table_attrs = self.html_attrs(
            border='0',
            cellpadding='0',
            cellspacing='0',
            role='presentation',
            style='inner-table',
        )

        return f'''
            <!--[if mso | IE]>
                <table {mso_table_attrs}>
                    <tr>
                        <td {self.html_attrs(style='outlook-inner-td')}>
            <![endif]-->
                <div {div_attrs}>
                    <table {inner_table_attrs}>
                        <tbody>
                            <tr>
                                <td {self.html_attrs(style='inner-td')} >
                                    <table {inner_table_attrs}>
                                        <tbody>
                                            {self.renderChildren(children, renderer=render_child)}
                                        </tbody>
                                    </table>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            <!--[if mso | IE]>
                        </td>
                    </tr>
                </table>
            <![endif]-->
        '''

    def renderMode(self):
        commonAttributes = {
            'background': self.getAttribute('background-url'),
            'style': 'hero',
        }
        mode = self.getAttribute('mode')
        if mode == 'fluid-height':
            magicTd = self.html_attrs(style='td-fluid')
            return f'''
                <td {magicTd} />
                <td {self.html_attrs(**commonAttributes)}>
                    {self.renderContent()}
                </td>
                <td {magicTd} />
            '''
        else:
            height_attr = parse_int(self.getAttribute('height'))
            padding_top = self.getShorthandAttrValue('padding', 'top')
            paddig_bottom = self.getShorthandAttrValue('padding', 'bottom')
            height = height_attr - padding_top - paddig_bottom
            return f'''
                <td {self.html_attrs(**commonAttributes, height=height)}>
                    {self.renderContent()}
                </td>
            '''


    def render(self):
        containerWidth = self.context['containerWidth']

        mso_table_attrs = self.html_attrs(
            align='center',
            border='0',
            cellpadding='0',
            cellspacing='0',
            role='presentation',
            style='outlook-table',
            width=parse_int(containerWidth),
        )
        image_attrs = self.html_attrs(
            style='outlook-image',
            src=self.getAttribute('background-url'),
            **{'xmlns:v': 'urn:schemas-microsoft-com:vml'},
        )
        div_attrs = self.html_attrs(
            align=self.getAttribute('align', missing_ok=True),
            class_=self.getAttribute('css-class', missing_ok=True),
            style='div',
        )
        table_attrs = self.html_attrs(
            border='0',
            cellpadding='0',
            cellspacing='0',
            role='presentation',
            style='table',
        )

        return f'''
            <!--[if mso | IE]>
                <table {mso_table_attrs}>
                    <tr>
                        <td {self.html_attrs(style='outlook-td')}>
                            <v:image {image_attrs} />
            <![endif]-->
            <div {div_attrs}>
                <table {table_attrs}>
                    <tbody>
                        <tr {self.html_attrs(style='tr')}>
                            {self.renderMode()}
                        </tr>
                    </tbody>
                </table>
            </div>
            <!--[if mso | IE]>
                        </td>
                    </tr>
                </table>
            <![endif]-->
        '''


def makeBackgroundString(parts):
    return ' '.join(filter(None, parts))
