
from ._head_base import HeadComponent


__all__ = ['MjTitle']

class MjTitle(HeadComponent):
    component_name = 'mj-title'

    def handler(self):
        add = self.context['add']
        add('title', self.getContent())
