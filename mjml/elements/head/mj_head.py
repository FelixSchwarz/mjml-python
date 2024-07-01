import typing as t

import typing_extensions as te

from ._head_base import HeadComponent


__all__ = ['MjHead']

class MjHead(HeadComponent):
    component_name: t.ClassVar[str] = 'mj-head'

    @te.override
    def handler(self) -> t.Optional[str]:
        # TODO typing: fix
        return self.handlerChildren()
