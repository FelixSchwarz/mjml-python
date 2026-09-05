
from collections.abc import Mapping
from enum import Enum
from typing import Any, ClassVar, Optional, Union

from mjml.helpers.format_attributes import formatAttributes


__all__ = ['initComponent', 'ComponentCategory', 'Component', 'GLOBAL_ATTRS']

# attributes every element accepts, so no component declares them
GLOBAL_ATTRS = frozenset({'mj-class', 'css-class'})


class ComponentCategory(Enum):
    """
    What a component is, so a parent can say which children it takes.
    """
    HEAD_ELEMENT = 'head-element'
    SECTION_LEVEL = 'section-level'
    COLUMN_LEVEL = 'column-level'
    BODY_ELEMENT = 'body-element'
    RAW = 'raw'
    # only "mj-attributes": it declares defaults for every element there is
    ANY = 'any'

def initComponent(
    name: Optional[str],
    components: Mapping[str, type["Component"]],
    **initialDatas: Any,
) -> Optional["Component"]:
    if name is None:
        return None
    component_cls = components.get(name)
    if not component_cls:
        return None

    component = component_cls(**initialDatas)
    if getattr(component, 'headStyle', None):
        component.context['addHeadStyle'](name, component.headStyle)
    componentHeadStyle = getattr(component, 'componentHeadStyle', None)
    if componentHeadStyle:
        component.context['addComponentHeadSyle'](componentHeadStyle)
    return component


# Most head components just modify global data structures and return None
# but "mj-head" returns the rendered output of all its children as tuple.
HandlerResult = Union[str, tuple[Optional[str], ...], None]


class Component:
    component_name: ClassVar[str]
    # the content of an ending tag is raw text/HTML, not MJML
    ending_tag: ClassVar[bool] = False
    # which groups this component belongs to
    categories: ClassVar[frozenset[ComponentCategory]] = frozenset()
    # categories and tag names this component takes as children
    accepts: ClassVar[frozenset[Union[ComponentCategory, str]]] = frozenset()

    # LATER: not sure upstream also passes tagName, makes code easier for us
    def __init__(self, *, attributes=None, children=(), content: str='',
                 context: Mapping[str, Any],
                 props: Optional[dict[str, Any]]=None,
                 globalAttributes: Optional[dict[str, Any]]=None,
                 headStyle: Optional[Any]=None,
                 tagName: Optional[str]=None) -> None:
        self.children = list(children)
        self.content = content
        self.context = context
        self.tagName = tagName

        self.props: dict[str, Any] = {**(props or {}), 'children': children, 'content': content}

        self.attrs = formatAttributes(
            {
                **self.default_attrs(),
                **(globalAttributes or {}),
                **(attributes or {}),
            },
            self.allowed_attrs(),
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
    def allowed_attrs(cls) -> Mapping[str, str]:
        return {}

    def getContent(self) -> str:
        # Actually "self.content" should not be None but sometimes it is
        # (probably due to bugs in this Python port). This special guard
        # clause is the final fix to render the "welcome-email.mjml" from
        # mjml's "email-templates" repo.
        if self.content is None:
            return ''
        return self.content.strip()

    def getChildContext(self) -> Mapping[str, Any]:
        return self.context

    # js: getAttribute(name)
    def get_attr(self, name: str, *, missing_ok: bool=False) -> Optional[Any]:
        is_allowed_attr = (name in self.allowed_attrs()) or (name in GLOBAL_ATTRS)
        is_default_attr = name in self.default_attrs()
        if not missing_ok and (not is_allowed_attr) and (not is_default_attr):
            raise AssertionError(f'{self.__class__.__name__} has no declared attr {name}')
        return self.attrs.get(name)
    getAttribute = get_attr

    def handler(self) -> HandlerResult:
        return None

    def render(self) -> str:
        return ''
