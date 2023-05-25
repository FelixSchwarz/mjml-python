

from ..helpers import suffixCssClasses, widthParser
from ._base import BodyComponent


__all__ = ['MjCarouselImage']


class MjCarouselImage(BodyComponent):
    component_name = 'mj-carousel-image'

    @classmethod
    def allowed_attrs(cls):
        return {
            'alt'             : 'string',
            'href'            : 'string',
            'rel'             : 'string',
            'target'          : 'string',
            'title'           : 'string',
            'src'             : 'string',
            'thumbnails-src'  : 'string',
            'border-radius'   : 'unit(px,%){1,4}',
            'tb-border'       : 'string',
            'tb-border-radius': 'unit(px,%){1,4}',
        }

    @classmethod
    def default_attrs(cls):
        return {
            'target': '_blank',
        }

    def get_styles(self):
        return {
            'images'    : {
                'img'          : {
                    'border-radius': self.getAttribute('border-radius'),
                    'display'      : 'block',
                    'width'        : self.context['containerWidth'],
                    'max-width'    : '100%',
                    'height'       : 'auto',
                },
                'firstImageDiv': {},
                'otherImageDiv': {
                    'display' : 'none',
                    'mso-hide': 'all',
                },
            },
            'radio'     : {
                'input': {
                    'display' : 'none',
                    'mso-hide': 'all',
                },
            },
            'thumbnails': {
                'a'  : {
                    'border'       : self.getAttribute('tb-border'),
                    'border-radius': self.getAttribute('tb-border-radius'),
                    'display'      : 'inline-block',
                    'overflow'     : 'hidden',
                    'width'        : self.getAttribute('tb-width', missing_ok=True),
                },
                'img': {
                    'display': 'block',
                    'width'  : '100%',
                    'height' : 'auto',
                },
            },
        }

    def renderThumbnail(self):
        carouselId = self.getAttribute('carouselId', missing_ok=True)
        width, _ = widthParser(self.getAttribute('tb-width', missing_ok=True))
        imgIndex = self.props['index'] + 1
        cssClass = suffixCssClasses(
            self.getAttribute('css-class', missing_ok=True),
            'thumbnail',
        )

        a_attrs = self.html_attrs(
            style='thumbnails.a',
            href=f'#{imgIndex}',
            target=self.getAttribute('target'),
            class_=f'mj-carousel-thumbnail mj-carousel-{carouselId}-thumbnail mj-carousel-{carouselId}-thumbnail-{imgIndex} {cssClass}' # noqa: E501
        )
        img_attrs = self.html_attrs(
            style='thumbnails.img',
            src=self.getAttribute('thumbnails-src') or self.getAttribute('src'),
            alt=self.getAttribute('alt'),
            width=width,
        )

        return f'''
            <a {a_attrs}>
                <label {self.html_attrs(for_=f'mj-carousel-{carouselId}-radio-{imgIndex}')}>
                    <img {img_attrs}/>
                </label>
            </a>
        '''

    def renderRadio(self):
        index = self.props['index']
        carousel_id = self.getAttribute('carouselId', missing_ok=True)
        _c_radio_class_str = f'mj-carousel-{carousel_id}-radio'
        input_attrs = self.html_attrs(
            class_  = f'mj-carousel-radio {_c_radio_class_str} {_c_radio_class_str}-{index + 1}',
            checked = 'checked' if index == 0 else None,
            type    = 'radio',
            name    = f'mj-carousel-radio-{carousel_id}',
            id      = f'{_c_radio_class_str}-{index + 1}',
            style   = 'radio.input',
        )
        return f'<input {input_attrs} />'

    def render(self):
        index = self.props['index']
        css_class = self.getAttribute('css-class', missing_ok=True) or ''
        div_attrs = self.html_attrs(
            class_ = f'mj-carousel-image mj-carousel-image-{index + 1} {css_class}',
            style  = 'images.firstImageDiv' if index == 0 else 'images.otherImageDiv',
        )

        img_attrs = self.html_attrs(
            title  = self.getAttribute('title'),
            src    = self.getAttribute('src'),
            alt    = self.getAttribute('alt'),
            style  = 'images.img',
            width  = widthParser(self.context['containerWidth'])[0],
            border = '0',
        )
        image = f'<img {img_attrs} />'
        href = self.getAttribute('href')
        if href:
            rel = self.getAttribute('rel')
            div_content = f'<a {self.html_attrs(href=href, rel=rel, target="_blank")}>{image}</a>'
        else:
            div_content = image

        return f'<div {div_attrs}>{div_content}</div>'
