
from ._head_base import HeadComponent


__all__ = ['MjHead']

class MjHead(HeadComponent):
    def handler(self):
        return self.handlerChildren()

