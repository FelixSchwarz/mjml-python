from typing import ClassVar

from typing_extensions import override

from ._head_base import HeadComponent


__all__ = ['MjBreakpoint']


class MjBreakpoint(HeadComponent):
    component_name: ClassVar[str] = 'mj-breakpoint'

    @override
    @classmethod
    def allowed_attrs(cls) -> dict[str, str]:
        return {
            'width': 'unit(px)',
        }

    @override
    def handler(self) -> None:
        add = self.context['add']
        add('breakpoint', self.getAttribute('width'))
