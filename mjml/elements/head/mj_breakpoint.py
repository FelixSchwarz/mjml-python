import typing as t

import typing_extensions as te

from ._head_base import HeadComponent


__all__ = ['MjBreakpoint']


class MjBreakpoint(HeadComponent):
    component_name: t.ClassVar[str] = 'mj-breakpoint'

    @te.override
    @classmethod
    def allowed_attrs(cls) -> t.Dict[str, str]:
        return {
            'width': 'unit(px)',
        }

    @te.override
    def handler(self) -> None:
        add = self.context['add']
        add('breakpoint', self.getAttribute('width'))
