from typing import ClassVar

from typing_extensions import override

from mjml.core import ComponentCategory

from ._head_base import HeadComponent


__all__ = ['MjFont']


class MjFont(HeadComponent):
    component_name: ClassVar[str] = 'mj-font'
    categories = frozenset({ComponentCategory.HEAD_ELEMENT})

    @override
    @classmethod
    def allowed_attrs(cls) -> dict[str, str]:
        return {
            'href'            : 'string',
            'name'            : 'string',
        }

    @override
    def handler(self) -> None:
        add = self.context['add']
        add('fonts', self.getAttribute('name'), self.getAttribute('href'))
