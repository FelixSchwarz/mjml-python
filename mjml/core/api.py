
from collections.abc import Mapping
from typing import Any, ClassVar, Optional, Union

from ..lib import merge_dicts
from .registry import components


__all__ = ['initComponent', 'Component']

def initComponent(
    name: Optional[str],
    **initialDatas: Any,
) -> Optional["Component"]:
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
    component_name: ClassVar[str]

    # LATER: not sure upstream also passes tagName, makes code easier for us
    def __init__(self, *, attributes=None, children=(), content: str='',
                 context: Optional[Mapping[str, Any]],
                 props: Optional[dict[str, Any]]=None,
                 globalAttributes: Optional[dict[str, Any]]=None,
                 headStyle: Optional[Any]=None,
                 tagName: Optional[str]=None) -> None:
        self.children = list(children)
        self.content = content
        self.context = context
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
    def default_attrs(cls) -> dict[str, Any]:
        return {}

    # js: static allowedAttributes
    @classmethod
    def allowed_attrs(cls) -> Mapping[str, Union[str, None]]:
        return {}

    def getContent(self) -> str:
        # Actually "self.content" should not be None but sometimes it is
        # (probably due to bugs in this Python port). This special guard
        # clause is the final fix to render the "welcome-email.mjml" from
        # mjml's "email-templates" repo.
        if self.content is None:
            return ''
        return self.content.strip()

    def getChildContext(self) -> dict[str, Any]:
        return self.context

    # js: getAttribute(name)
    def get_attr(self, name: str, *, missing_ok: bool=False) -> Optional[Any]:
        is_allowed_attr = name in self.allowed_attrs()
        is_default_attr = name in self.default_attrs()
        if not missing_ok and (not is_allowed_attr) and (not is_default_attr):
            raise AssertionError(f'{self.__class__.__name__} has no declared attr {name}')
        return self.attrs.get(name)
    getAttribute = get_attr

    def handler(self) -> Optional[str]:
        return None

    def render(self) -> str:
        return ''
