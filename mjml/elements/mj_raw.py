
from ._base import BodyComponent


__all__ = ['MjRaw']


class MjRaw(BodyComponent):
    rawElement = True

    def render(self):
        return self.getContent()
