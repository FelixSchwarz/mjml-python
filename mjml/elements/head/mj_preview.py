
from ._head_base import HeadComponent


__all__ = ['MjPreview']


class MjPreview(HeadComponent):
    component_name = 'mj-preview'

    def handler(self):
        add = self.context['add']
        add('preview', self.getContent())
