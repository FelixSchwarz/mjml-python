
from ._head_base import HeadComponent


__all__ = ['MjFont']


class MjFont(HeadComponent):
    component_name = 'mj-font'

    @classmethod
    def allowed_attrs(cls):
        return {
            'href'            : 'string',
            'name'            : 'string',
        }

    def handler(self):
        add = self.context['add']
        add('fonts', self.getAttribute('name'), self.getAttribute('href'))
