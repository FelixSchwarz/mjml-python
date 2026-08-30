
from ._base import BodyComponent


__all__ = ['MjRaw']


class MjRaw(BodyComponent):
    component_name = 'mj-raw'
    ending_tag = True

    rawElement = True

    def render(self):
        return self.getContent()
