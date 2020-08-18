

from ..lib import merge_dicts
from ..core import initComponent, Component
from ..core.registry import _components
from ..helpers import *


__all__ = [
    'BodyComponent',
]

class BodyComponent(Component):
    def render(self):
        raise NotImplementedError(f'{self.__cls__.__name__} should override ".render()"')

    def getShorthandAttrValue(self, attribute, direction):
        mjAttributeDirection = self.getAttribute(f'{attribute}-{direction}')
        mjAttribute = self.getAttribute(attribute)

        if mjAttributeDirection:
            return strip_unit(mjAttributeDirection)
        if not mjAttribute:
            return 0
        return shorthandParser(mjAttribute, direction)

    def getShorthandBorderValue(self, direction):
        borderDirection = direction and self.getAttribute(f'border-{direction}')
        border = self.getAttribute('border')
        return borderParser(borderDirection or border or '0')

    def getBoxWidths(self):
        containerWidth = self.context['containerWidth']
        parsedWidth = strip_unit(containerWidth)
        paddings = self.getShorthandAttrValue('padding', 'right') + self.getShorthandAttrValue('padding', 'left')
        borders = self.getShorthandBorderValue('right') + self.getShorthandBorderValue('left')

        return {
            'totalWidth': parsedWidth,
            'borders'   : borders,
            'paddings'  : paddings,
            'box'       : parsedWidth - paddings - borders,
        }

    # js: htmlAttributes(attributes)
    def html_attrs(self, **attrs):
        def _to_str(kv):
            key, value = kv
            if key == 'style':
                value = self.styles(value)
            if key == 'class_':
                key = 'class'
            return f'{key}="{value}"' if is_not_empty(value) else None
        serialized_attrs = map(_to_str, attrs.items())
        return ' '.join(filter(None, serialized_attrs))

    # js: getStyles()
    def get_styles(self):
        return {}

    # js: styles(styles)
    def styles(self, key=None):
        _styles = None
        if key and isinstance(key, str):
            _styles_dict = self.get_styles()
            _styles = _styles_dict.get(key)
            if _styles and not isinstance(_styles, dict):
                raise ValueError(f'key={key}')
        elif key:
            # predefined dict
            _styles = key
        if not _styles:
            _styles = {}

        def serializer(kv):
            k, v = kv
            return f'{k}:{v}' if is_not_empty(v) else None
        style_attr_strs = filter(None, map(serializer, _styles.items()))
        style_str = ';'.join(style_attr_strs)
        return style_str

    def renderChildren(self, childrens=None, props=None, renderer=None, attributes=None, rawXML=False):
        if not props:
            props = {}
        if not renderer:
            renderer = lambda component: component.render()
        if not attributes:
            attributes = {}
        childrens = childrens or self.props.children

        if rawXML:
            # return childrens.map(child => jsonToXML(child)).join('\n')
            raise NotImplementedError
        sibling = len(childrens)

        # code to calculate "nonRawSiblings" seemed too compressed/complicated
        # to me (traded readability for fewer lines of code) so the Python code
        # looks quite a bit different. However the final HTML looks the same
        # so I guess I got it right somehow :-)
        #
        # upstream:
        # const rawComponents = filter(components, c => c.isRawElement())
        # const nonRawSiblings = childrens.filter(
        #  child => !find(rawComponents, c => c.getTagName() === child.tagName),
        #).length
        raw_tag_names = set()
        for tag_name, component in _components().items():
            if component.isRawElement():
                raw_tag_names.add(tag_name)
        is_raw_element = lambda c: (c['tagName'] in raw_tag_names)

        _nonRawSiblings = []
        for child in childrens:
            if (child is None) or is_raw_element(child):
                continue
            _nonRawSiblings.append(child)
        nonRawSiblings = len(_nonRawSiblings)

        output = ''
        index = 0
        for children in childrens:
            if children is None:
                # "comment" node
                continue
            child_props = merge_dicts(props, {
                'first': (index == 0),
                'index': index,
                'last': (index+1 == sibling),
                'sibling': sibling,
                'nonRawSiblings': nonRawSiblings,
            })
            initialDatas = merge_dicts(children,{
                'attributes': merge_dicts(attributes, children['attributes']),
                'context': self.getChildContext(),
                'props': child_props,
            })
            initialDatas.pop('tagName')

            component = initComponent(
                name = children['tagName'],
                **initialDatas,
            )
            if component:
                output += renderer(component)
            index += 1
        return output

