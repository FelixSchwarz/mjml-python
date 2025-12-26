from typing import ClassVar

from typing_extensions import override

from ._head_base import HeadComponent


__all__ = ['MjPreview']


class MjPreview(HeadComponent):
    component_name: ClassVar[str] = 'mj-preview'

    @override
    def handler(self) -> None:
        add = self.context['add']
        add('preview', self.getContent())
