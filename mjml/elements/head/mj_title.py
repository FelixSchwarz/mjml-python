
from ._head_base import HeadComponent


__all__ = ['MjTitle']

class MjTitle(HeadComponent):
    def handler(self):
        add = self.context['add']
        add('title', self.getContent())

