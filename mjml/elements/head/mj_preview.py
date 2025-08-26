import typing as t

import typing_extensions as te

from ._head_base import HeadComponent


__all__ = ['MjPreview']


class MjPreview(HeadComponent):
    component_name: t.ClassVar[str] = 'mj-preview'

    @te.override
    def handler(self) -> None:
        add = self.context['add']
        add('preview', self.getContent())
