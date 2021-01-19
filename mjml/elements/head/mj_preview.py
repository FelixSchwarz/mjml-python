
from ._head_base import HeadComponent


__all__ = ['MjPreview']


class MjPreview(HeadComponent):

    def handler(self):
        add = self.context['add']
        add('preview', self.getContent())
