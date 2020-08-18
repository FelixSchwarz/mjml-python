
from ..lib import merge_dicts, AttrDict

from .registry import _components


__all__ = ['initComponent', 'Component']

def initComponent(name, **initialDatas):
    components = _components()
    component_cls = components[name]
    if not component_cls:
        return None

    component = component_cls(**initialDatas)
    if getattr(component, 'headStyle', None):
        component.context['addHeadStyle'](name, component.headStyle)
    if getattr(component, 'componentHeadStyle', None):
        component.context['addComponentHeadSyle'](component.componentHeadStyle)
    return component



class Component:
    # LATER: not sure upstream also passes tagName, makes code easier for us
    def __init__(self, *, attributes=None, children=(), content='', context=None, props=None, globalAttributes=None, headStyle=None, tagName=None, tail=''):
        self.children = list(children)
        self.content = content
        self.tail = tail
        self.context = context
        self.tagName = tagName

        self.props = AttrDict(merge_dicts(props, {'children': children, 'content': content}))

        # upstream also checks "self.allowed_attrs"
        self.attrs = merge_dicts(
            self.default_attrs(),
            globalAttributes or {},
            attributes or {},
        )

        # optional attributes (methods) for some components
        if headStyle:
            self.headStyle = headStyle

    @classmethod
    def getTagName(cls):
        cls_name = cls.__name__
        return cls_name

    @classmethod
    def isRawElement(cls):
        cls_value = getattr(cls, 'rawElement', None)
        return bool(cls_value)

    # js: static defaultAttributes
    @classmethod
    def default_attrs(cls):
        return {}

    def getContent(self):
        return self.content.strip()

    def getChildContext(self):
        return self.context

    # js: getAttribute(name)
    def get_attr(self, name):
        # assert name in allowed_attrs
        return self.attrs[name]
    getAttribute = get_attr

    def render(self):
        return ''

