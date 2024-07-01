import typing as t

import typing_extensions as te

from ._head_base import HeadComponent


__all__ = ['MjTitle']

class MjTitle(HeadComponent):
    component_name: t.ClassVar[str] = 'mj-title'

    @te.override
    def handler(self) -> None:
        add = self.context['add']
        add('title', self.getContent())
