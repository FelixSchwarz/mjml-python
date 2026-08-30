
from mjml.core import ComponentCategory

from ._base import BodyComponent


__all__ = ['MjRaw']


class MjRaw(BodyComponent):
    component_name = 'mj-raw'
    categories = frozenset({ComponentCategory.RAW})
    ending_tag = True

    rawElement = True

    def render(self):
        return self.getContent()
