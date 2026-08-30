from typing import ClassVar

from typing_extensions import override

from mjml.core import ComponentCategory

from ._head_base import HeadComponent


__all__ = ['MjPreview']


class MjPreview(HeadComponent):
    component_name: ClassVar[str] = 'mj-preview'
    categories = frozenset({ComponentCategory.HEAD_ELEMENT})
    ending_tag = True

    @override
    def handler(self) -> None:
        add = self.context['add']
        add('preview', self.getContent())
