
from ..helpers import widthParser
from ._base import BodyComponent


__all__ = ['MjSocialElement']

IMG_BASE_URL = 'https://www.mailjet.com/images/theme/v1/icons/ico-social/'

defaultSocialNetworks = {
    'facebook'  : {
        'share-url'       : 'https://www.facebook.com/sharer/sharer.php?u=[[URL]]',
        'background-color': '#3b5998',
        'src'             : f'{IMG_BASE_URL}facebook.png',
    },
    'twitter'   : {
        'share-url'       : 'https://twitter.com/intent/tweet?url=[[URL]]',
        'background-color': '#55acee',
        'src'             : f'{IMG_BASE_URL}twitter.png',
    },
    'google'    : {
        'share-url'       : 'https://plus.google.com/share?url=[[URL]]',
        'background-color': '#dc4e41',
        'src'             : f'{IMG_BASE_URL}google-plus.png',
    },
    'pinterest' : {
        'share-url'       :
            'https://pinterest.com/pin/create/button/?url=[[URL]]&media=&description=',
        'background-color': '#bd081c',
        'src'             : f'{IMG_BASE_URL}pinterest.png',
    },
    'linkedin'  : {
        'share-url'       :
            'https://www.linkedin.com/shareArticle?mini=true&url=[[URL]]&title=&summary=&source=',
        'background-color': '#0077b5',
        'src'             : f'{IMG_BASE_URL}linkedin.png',
    },
    'instagram' : {
        'background-color': '#3f729b',
        'src'             : f'{IMG_BASE_URL}instagram.png',
    },
    'web'       : {
        'src'             : f'{IMG_BASE_URL}web.png',
        'background-color': '#4BADE9',
    },
    'snapchat'  : {
        'src'             : f'{IMG_BASE_URL}snapchat.png',
        'background-color': '#FFFA54',
    },
    'youtube'   : {
        'src'             : f'{IMG_BASE_URL}youtube.png',
        'background-color': '#EB3323',
    },
    'tumblr'    : {
        'src'             : f'{IMG_BASE_URL}tumblr.png',
        'share-url'       :
            'https://www.tumblr.com/widgets/share/tool?canonicalUrl=[[URL]]',
        'background-color': '#344356',
    },
    'github'    : {
        'src'             : f'{IMG_BASE_URL}github.png',
        'background-color': '#000000',
    },
    'xing'      : {
        'src'             : f'{IMG_BASE_URL}xing.png',
        'share-url'       : 'https://www.xing.com/app/user?op=share&url=[[URL]]',
        'background-color': '#296366',
    },
    'vimeo'     : {
        'src'             : f'{IMG_BASE_URL}vimeo.png',
        'background-color': '#53B4E7',
    },
    'medium'    : {
        'src'             : f'{IMG_BASE_URL}medium.png',
        'background-color': '#000000',
    },
    'soundcloud': {
        'src'             : f'{IMG_BASE_URL}soundcloud.png',
        'background-color': '#EF7F31',
    },
    'dribbble'  : {
        'src'             : f'{IMG_BASE_URL}dribbble.png',
        'background-color': '#D95988',
    },
}

for key, value in list(defaultSocialNetworks.items()):
    defaultSocialNetworks[f'{key}-noshare'] = {
        **value,
        'share-url': '[[URL]]',
    }


class MjSocialElement(BodyComponent):
    component_name = 'mj-social-element'

    @classmethod
    def allowed_attrs(cls):
        return {
            'align'           : 'enum(left,center,right)',
            'background-color': 'color',
            'color'           : 'color',
            'border-radius'   : 'unit(px)',
            'font-family'     : 'string',
            'font-size'       : 'unit(px)',
            'font-style'      : 'string',
            'font-weight'     : 'string',
            'href'            : 'string',
            'icon-size'       : 'unit(px,%)',
            'icon-height'     : 'unit(px,%)',
            'icon-padding'    : 'unit(px,%){1,4}',
            'line-height'     : 'unit(px,%,)',
            'name'            : 'string',
            'padding-bottom'  : 'unit(px,%)',
            'padding-left'    : 'unit(px,%)',
            'padding-right'   : 'unit(px,%)',
            'padding-top'     : 'unit(px,%)',
            'padding'         : 'unit(px,%){1,4}',
            'text-padding'    : 'unit(px,%){1,4}',
            'rel'             : 'string',
            'src'             : 'string',
            'srcset'          : 'string',
            'sizes'           : 'string',
            'alt'             : 'string',
            'title'           : 'string',
            'target'          : 'string',
            'text-decoration' : 'string',
            'vertical-align'  : 'enum(top,middle,bottom)',
        }

    @classmethod
    def default_attrs(cls):
        return {
            'align'          : 'left',
            'color'          : '#000',
            'border-radius'  : '3px',
            'font-family'    : 'Ubuntu, Helvetica, Arial, sans-serif',
            'font-size'      : '13px',
            'line-height'    : '1',
            'padding'        : '4px',
            'text-padding'   : '4px 4px 4px 0',
            'target'         : '_blank',
            'text-decoration': 'none',
            'vertical-align' : 'middle',
        }

    # js: getStyles()
    def get_styles(self):
        attributes = self.getSocialAttributes()
        iconSize = attributes['icon-size']
        iconHeight = attributes['icon-height']
        backgroundColor = attributes['background-color']

        return {
            'td'    : {
                'padding'       : self.getAttribute('padding'),
                'vertical-align': self.getAttribute('vertical-align'),
            },
            'table' : {
                'background'   : backgroundColor,
                'border-radius': self.getAttribute('border-radius'),
                'width'        : iconSize,
            },
            'icon'  : {
                'padding'       : self.getAttribute('icon-padding'),
                'font-size'     : '0',
                'height'        : iconHeight or iconSize,
                'vertical-align': 'middle',
                'width'         : iconSize,
            },
            'img'   : {
                'border-radius': self.getAttribute('border-radius'),
                'display'      : 'block',
            },
            'tdText': {
                'vertical-align': 'middle',
                'padding'       : self.getAttribute('text-padding'),
            },
            'text'  : {
                'color'          : self.getAttribute('color'),
                'font-size'      : self.getAttribute('font-size'),
                'font-weight'    : self.getAttribute('font-weight'),
                'font-style'     : self.getAttribute('font-style'),
                'font-family'    : self.getAttribute('font-family'),
                'line-height'    : self.getAttribute('line-height'),
                'text-decoration': self.getAttribute('text-decoration'),
            },
        }

    def getSocialAttributes(self):
        socialNetwork = defaultSocialNetworks.get(self.getAttribute('name'), {})
        href = self.getAttribute('href')

        if href and socialNetwork.get('share-url'):
            href = socialNetwork.get('share-url', '').replace('[[URL]]', href)

        attrs = {}
        attr_names = ['icon-size', 'icon-height', 'srcset', 'sizes', 'src', 'background-color']
        for attr in attr_names:
            attrs[attr] = self.getAttribute(attr) or socialNetwork.get(attr)
        return {'href': href, **attrs}

    def render(self):
        attributes = self.getSocialAttributes()
        iconSize = attributes['icon-size']
        iconHeight = attributes['icon-height']
        hasLink = bool(self.getAttribute('href'))

        def get_img():
            height, _ = widthParser(iconHeight or iconSize)
            width, _ = widthParser(iconSize)
            img_attrs = self.html_attrs(
                alt    = self.getAttribute('alt'),
                title  = self.getAttribute('title'),
                height = height,
                src    = attributes['src'],
                style  = 'img',
                width  = width,
                sizes  = attributes['sizes'],
                srcset = attributes['srcset'],
            )
            img = f'<img {img_attrs} />'

            if hasLink:
                link_attrs = self.html_attrs(
                    href   = attributes['href'],
                    rel    = self.getAttribute('rel'),
                    target = self.getAttribute('target'),
                )
                return f'<a {link_attrs}>{img}</a>'
            return img

        def get_text(content):
            if hasLink:
                link_attrs = self.html_attrs(
                    href   = attributes['href'],
                    style  = 'text',
                    rel    = self.getAttribute('rel'),
                    target = self.getAttribute('target'),
                )
                return f'<a {link_attrs}>{content}</a>'

            return f'<span {self.html_attrs(style="text")}>{content}</span>'

        content_html = ''
        content = self.getContent()
        if content:
            content_html = f'''
                <td {self.html_attrs(style='tdText')}>
                    {get_text(content)}
                </td>
            '''

        table_attrs = self.html_attrs(
            border      = '0',
            cellpadding = '0',
            cellspacing = '0',
            role        = 'presentation',
            style       = 'table',
        )
        return f'''
            <tr {self.html_attrs(class_=self.getAttribute('css-class', missing_ok=True))}>
                <td {self.html_attrs(style='td')}>
                    <table {table_attrs}>
                        <tbody>
                            <tr>
                                <td {self.html_attrs(style='icon')}>
                                    {get_img()}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </td>
                {content_html}
            </tr>
        '''
