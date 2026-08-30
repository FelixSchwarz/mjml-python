
from typing import ClassVar, Optional

from typing_extensions import override

from mjml.core import ComponentCategory

from ._head_base import HeadComponent


__all__ = ['MjHead']

class MjHead(HeadComponent):
    component_name: ClassVar[str] = 'mj-head'
    accepts = frozenset({ComponentCategory.HEAD_ELEMENT, ComponentCategory.RAW})

    @override
    def handler(self) -> tuple[Optional[str], ...]:
        return self.handlerChildren()
