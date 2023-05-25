
import random
import string
from itertools import repeat

from ..helpers import msoConditionalTag, widthParser
from ._base import BodyComponent


__all__ = ['MjCarousel']


class MjCarousel(BodyComponent):
    component_name = 'mj-carousel'

    @classmethod
    def allowed_attrs(cls):
        return {
            'align'                     : 'enum(left,center,right)',
            'border-radius'             : 'unit(px,%){1,4}',
            'container-background-color': 'color',
            'icon-width'                : 'unit(px,%)',
            'left-icon'                 : 'string',
            'padding'                   : 'unit(px,%){1,4}',
            'padding-top'               : 'unit(px,%)',
            'padding-bottom'            : 'unit(px,%)',
            'padding-left'              : 'unit(px,%)',
            'padding-right'             : 'unit(px,%)',
            'right-icon'                : 'string',
            'thumbnails'                : 'enum(visible,hidden)',
            'tb-border'                 : 'string',
            'tb-border-radius'          : 'unit(px,%)',
            'tb-hover-border-color'     : 'color',
            'tb-selected-border-color'  : 'color',
            'tb-width'                  : 'unit(px,%)',
        }

    @classmethod
    def default_attrs(cls):
        return {
            'align'                   : 'center',
            'border-radius'           : '6px',
            'icon-width'              : '44px',
            'left-icon'               : 'https://i.imgur.com/xTh3hln.png',
            'right-icon'              : 'https://i.imgur.com/os7o9kz.png',
            'thumbnails'              : 'visible',
            'tb-border'               : '2px solid transparent',
            'tb-border-radius'        : '6px',
            'tb-hover-border-color'   : '#fead0d',
            'tb-selected-border-color': '#ccc',
        }

    carouselId = ''.join(random.choices(string.digits, k=16))

    def componentHeadStyle(self, breakpoint):
        length = len(self.props['children'])
        carouselId = self.carouselId

        if not length:
            return ''

        def buildCssSelectors(parent, repeatCount, sibling):
            def _selector_str(i):
                return f'{parent(i)} {repeat("+ * ", repeatCount(i))}+ {sibling(i)}'
            _selectors = [_selector_str(i) for i in range(length)]
            return ','.join(_selectors)

        carouselCss = f'''
            .mj-carousel {{
                -webkit-user-select: none;
                -moz-user-select: none;
                user-select: none;
            }}

            .mj-carousel-{carouselId}-icons-cell {{
                display: table-cell !important;
                width: {self.getAttribute('icon-width')} !important;
            }}

            .mj-carousel-radio,
            .mj-carousel-next,
            .mj-carousel-previous {{
                display: none !important;
            }}

            .mj-carousel-thumbnail,
            .mj-carousel-next,
            .mj-carousel-previous {{
                touch-action: manipulation;
            }}

            {buildCssSelectors(
                lambda i: f'.mj-carousel-{carouselId}-radio:checked',
                lambda i: i,
                lambda i: '.mj-carousel-content .mj-carousel-image'
            )} {{
                display: none !important;
            }}

            {buildCssSelectors(
                lambda i: f'.mj-carousel-{carouselId}-radio-{i + 1}:checked',
                lambda i: length - i - 1,
                lambda i: f'.mj-carousel-content .mj-carousel-image-{i + 1}'
            )} {{
                display: block !important;
            }}

            .mj-carousel-previous-icons,
            .mj-carousel-next-icons,
            {buildCssSelectors(
                lambda i: f'.mj-carousel-{carouselId}-radio-{i + 1}:checked',
                lambda i: length - i - 1,
                lambda i: f'.mj-carousel-content .mj-carousel-next-{((i + (1 % length) + length) % length) + 1}'
            )},
            {buildCssSelectors(
                lambda i: f'.mj-carousel-{carouselId}-radio-{i + 1}:checked',
                lambda i: length - i - 1,
                lambda i: f'.mj-carousel-content .mj-carousel-previous-{((i - (1 % length) + length) % length) + 1}'
            )} {{
                display: block !important;
            }}

            {buildCssSelectors(
                lambda i: f'.mj-carousel-{carouselId}-radio-{i + 1}:checked',
                lambda i: length - i - 1,
                lambda i: f'.mj-carousel-content .mj-carousel-{carouselId}-thumbnail-{i + 1}'
            )} {{
                border-color: {self.getAttribute('tb-selected-border-color')} !important;
            }}

            .mj-carousel-image img + div,
            .mj-carousel-thumbnail img + div {{
                display: none !important;
            }}

            {buildCssSelectors(
                lambda i: f'.mj-carousel-{carouselId}-thumbnail:hover',
                lambda i: length - i - 1,
                lambda i: '.mj-carousel-main .mj-carousel-image'
            )} {{
                display: none !important;
            }}

            .mj-carousel-thumbnail:hover {{
                border-color: {self.getAttribute('tb-hover-border-color')} !important;
            }}

            {buildCssSelectors(
                lambda i: f'.mj-carousel-{carouselId}-thumbnail-{i + 1}:hover',
                lambda i: length - i - 1,
                lambda i: f'.mj-carousel-main .mj-carousel-image-{i + 1}'
            )} {{
                display: block !important;
            }}
        ''' # noqa: E501

        fallback = f'''
            .mj-carousel noinput {{ display:block !important; }}
            .mj-carousel noinput .mj-carousel-image-1 {{ display: block !important;  }}
            .mj-carousel noinput .mj-carousel-arrows,
            .mj-carousel noinput .mj-carousel-thumbnails {{ display: none !important; }}

            [owa] .mj-carousel-thumbnail {{ display: none !important; }}

            @media screen yahoo {{
                .mj-carousel-{carouselId}-icons-cell,
                .mj-carousel-previous-icons,
                .mj-carousel-next-icons {{
                    display: none !important;
                }}

                {buildCssSelectors(
                    lambda i: f'.mj-carousel-{carouselId}-radio-1:checked',
                    lambda i: length - 1,
                    lambda i: f'.mj-carousel-content .mj-carousel-{carouselId}-thumbnail-1'
                )} {{
                    border-color: transparent;
                }}
            }}
        '''

        return f'{carouselCss}\n{fallback}'

    def get_styles(self):
        return {
            'carousel': {
                'div'  : {
                    'display'     : 'table',
                    'width'       : '100%',
                    'table-layout': 'fixed',
                    'text-align'  : 'center',
                    'font-size'   : '0px',
                },
                'table': {
                    'caption-side': 'top',
                    'display'     : 'table-caption',
                    'table-layout': 'fixed',
                    'width'       : '100%',
                },
            },
            'images'  : {
                'td': {
                    'padding': '0px',
                },
            },
            'controls': {
                'div': {
                    'display' : 'none',
                    'mso-hide': 'all',
                },
                'img': {
                    'display': 'block',
                    'width'  : self.getAttribute('icon-width'),
                    'height' : 'auto',
                },
                'td' : {
                    'font-size': '0px',
                    'display'  : 'none',
                    'mso-hide' : 'all',
                    'padding'  : '0px',
                },
            },
        }

    def thumbnailsWidth(self):
        childrenLen = len(self.props['children'])
        if not childrenLen:
            return 0
        parentWidth, _ = widthParser(self.context['containerWidth'])
        return self.getAttribute('tb-width') or f'{min([parentWidth / childrenLen, 110])}px'

    def imagesAttributes(self):
        return map(lambda c: c['attributes'], self.children)

    def generateRadios(self):
        children = self.props['children']

        return self.renderChildren(children,
            renderer=lambda component: component.renderRadio(),
            attributes={
                'carouselId': self.carouselId,
            },
        )

    def generateThumbnails(self):
        children = self.props['children']
        if self.getAttribute('thumbnails') != 'visible':
            return ''

        return self.renderChildren(children,
            attributes={
                'tb-border'       : self.getAttribute('tb-border'),
                'tb-border-radius': self.getAttribute('tb-border-radius'),
                'tb-width'        : self.thumbnailsWidth(),
                'carouselId'      : self.carouselId,
            },
            renderer=lambda component: component.renderThumbnail(),
        )

    def generateControls(self, direction, icon):
        iconWidth, _ = widthParser(self.getAttribute('icon-width'))

        img_attrs = self.html_attrs(
            src=icon,
            alt=direction,
            style='controls.img',
            width=iconWidth
        )
        content = ''.join(map(
            lambda i: f'''
                <label
                    {self.html_attrs(
                        for_=f'mj-carousel-{self.carouselId}-radio-{i}',
                        class_=f'mj-carousel-{direction} mj-carousel-{direction}-{i}',
                    )}
                >
                    <img {img_attrs} />
                </label>
            ''',
            range(1, len(self.props['children']) + 1)
        ))

        td_attrs = self.html_attrs(
            class_=f'mj-carousel-{self.carouselId}-icons-cell',
            style='controls.td',
        )
        div_attrs = self.html_attrs(
            class_=f'mj-carousel-{direction}-icons',
            style='controls.div',
        )
        return f'''
            <td {td_attrs}>
                <div {div_attrs}>
                    {content}
                </div>
            </td>
        '''

    def generateImages(self):
        return f'''
            <td {self.html_attrs(style='images.td')}>
                <div {self.html_attrs(class_='mj-carousel-images')}>
                    {self.renderChildren(self.props['children'],
                        attributes={
                            'border-radius': self.getAttribute('border-radius'),
                        },
                    )}
                </div>
            </td>
        '''

    def generateCarousel(self):
        table_attrs = self.html_attrs(
            style       = 'carousel.table',
            border      = '0',
            cellpadding = '0',
            cellspacing = '0',
            width       = '100%',
            role        = 'presentation',
            class_      = 'mj-carousel-main',
        )
        return f'''
            <table {table_attrs}>
                <tbody>
                    <tr>
                        {self.generateControls('previous', self.getAttribute('left-icon'))}
                        {self.generateImages()}
                        {self.generateControls('next', self.getAttribute('right-icon'))}
                    </tr>
                </tbody>
            </table>
        '''

    def renderFallback(self):
        children = self.props['children']

        if len(children) == 0:
            return ''

        return msoConditionalTag(
            self.renderChildren(
                [children[0]],
                attributes={
                    'border-radius': self.getAttribute('border-radius'),
                }
            )
        )

    def render(self):
        content_div_attrs = self.html_attrs(
            class_=f'mj-carousel-content mj-carousel-{self.carouselId}-content',
            style='carousel.div',
        )
        content = msoConditionalTag(
            f'''
                <div {self.html_attrs(class_='mj-carousel')}>
                    {self.generateRadios()}
                    <div {content_div_attrs}>
                        {self.generateThumbnails()}
                        {self.generateCarousel()}
                    </div>
                </div>
            ''',
            negation=True
        )
        return content + self.renderFallback()
