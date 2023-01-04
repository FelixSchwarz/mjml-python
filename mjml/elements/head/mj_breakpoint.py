
from ._head_base import HeadComponent


__all__ = ['MjBreakpoint']


class MjBreakpoint(HeadComponent):
    component_name = 'mj-breakpoint'

    @classmethod
    def allowed_attrs(cls):
        return {
            'width': 'unit(px)',
        }

    def handler(self):
        add = self.context['add']
        add('breakpoint', self.getAttribute('width'))
