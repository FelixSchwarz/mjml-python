import typing as t

from ..lib import merge_dicts
from .registry import components


__all__ = ['initComponent', 'Component']

def initComponent(name: t.Optional[str],
                  **initialDatas: t.Any) -> t.Optional["Component"]:
    if name is None:
        return None
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
    component_name: t.ClassVar[str]

    # LATER: not sure upstream also passes tagName, makes code easier for us
    def __init__(self, *, attributes=None, children=(), content: str='',
                 context: t.Optional[t.Dict[str, t.Any]]=None,
                 props: t.Optional[t.Dict[str, t.Any]]=None,
                 globalAttributes: t.Optional[t.Dict[str, t.Any]]=None,
                 headStyle: t.Optional[t.Any]=None,
                 tagName: t.Optional[str]=None) -> None:
        self.children = list(children)
        self.content = content
        # TODO typing: verify that this is the intent
        self.context = context or dict()
        self.tagName = tagName

        self.props = merge_dicts(props or {}, {'children': children, 'content': content})

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
    def getTagName(cls) -> str:
        cls_name = cls.__name__
        return cls_name

    @classmethod
    def isRawElement(cls) -> bool:
        cls_value = getattr(cls, 'rawElement', None)
        return bool(cls_value)

    # js: static defaultAttributes
    @classmethod
    def default_attrs(cls) -> t.Dict[str, t.Any]:
        return {}

    # js: static allowedAttributes
    @classmethod
    def allowed_attrs(cls) -> t.Dict[str, str]:
        return {}

    def getContent(self) -> str:
        # Actually "self.content" should not be None but sometimes it is
        # (probably due to bugs in this Python port). This special guard
        # clause is the final fix to render the "welcome-email.mjml" from
        # mjml's "email-templates" repo.
        if self.content is None:
            return ''
        return self.content.strip()

    def getChildContext(self) -> t.Dict[str, t.Any]:
        return self.context

    # js: getAttribute(name)
    def get_attr(self, name: str, *, missing_ok: bool=False) -> t.Optional[t.Any]:
        is_allowed_attr = name in self.allowed_attrs()
        is_default_attr = name in self.default_attrs()
        if not missing_ok and (not is_allowed_attr) and (not is_default_attr):
            raise AssertionError(f'{self.__class__.__name__} has no declared attr {name}')
        return self.attrs.get(name)
    getAttribute = get_attr

    def render(self) -> str:
        return ''
