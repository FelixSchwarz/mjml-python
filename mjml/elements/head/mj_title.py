from typing import ClassVar

from typing_extensions import override

from ._head_base import HeadComponent


__all__ = ['MjTitle']

class MjTitle(HeadComponent):
    component_name: ClassVar[str] = 'mj-title'

    @override
    def handler(self) -> None:
        add = self.context['add']
        add('title', self.getContent())
