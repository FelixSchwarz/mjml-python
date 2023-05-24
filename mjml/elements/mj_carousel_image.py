

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

        thumbnail_classes = [
            'mj-carousel-thumbnail',
            f'mj-carousel-{carouselId}-thumbnail',
            f'mj-carousel-{carouselId}-thumbnail-{imgIndex}',
            f'{cssClass}',
        ]
        a_attrs = self.html_attrs(
            style='thumbnails.a',
            href=f'#{imgIndex}',
            target=self.getAttribute('target'),
            class_=' '.join(thumbnail_classes)
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
        carouselId = self.getAttribute('carouselId', missing_ok=True)
        input_classes = [
            'mj-carousel-radio',
            f'mj-carousel-{carouselId}-radio',
            f'mj-carousel-{carouselId}-radio-{index + 1}',
        ]

        return f'''
            <input
                {self.html_attrs(
                    class_=' '.join(input_classes),
                    checked='checked' if index == 0 else None,
                    type='radio',
                    name=f'mj-carousel-radio-{carouselId}',
                    id=f'mj-carousel-{carouselId}-radio-{index + 1}',
                    style='radio.input',
                )}
            />
        '''

    def render(self):
        href = self.getAttribute('href')
        rel = self.getAttribute('rel')
        width, _ = widthParser(self.context['containerWidth'])
        index = self.props['index']

        image = f'''
            <img
                {self.html_attrs(
                    title=self.getAttribute('title'),
                    src=self.getAttribute('src'),
                    alt=self.getAttribute('alt'),
                    style='images.img',
                    width=width,
                    border='0',
                )}
            />
        '''

        if href:
            image = f'<a {self.html_attrs(href=href, rel=rel, target="_blank")}>{image}</a>'

        cssClass = self.getAttribute('css-class', missing_ok=True) or ''

        return f'''
            <div
                {self.html_attrs(
                    class_=f'mj-carousel-image mj-carousel-image-{index + 1} {cssClass}',
                    style='images.firstImageDiv' if index == 0 else 'images.otherImageDiv',
                )}
            >
                {image}
            </div>
        '''
