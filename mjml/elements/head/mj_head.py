
from typing import ClassVar, Optional

from typing_extensions import override

from ._head_base import HeadComponent


__all__ = ['MjHead']

class MjHead(HeadComponent):
    component_name: ClassVar[str] = 'mj-head'

    @override
    def handler(self) -> Optional[str]:
        return self.handlerChildren()
