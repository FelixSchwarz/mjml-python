
from ._head_base import HeadComponent


__all__ = ['MjHead']

class MjHead(HeadComponent):
    component_name = 'mj-head'

    def handler(self):
        return self.handlerChildren()
