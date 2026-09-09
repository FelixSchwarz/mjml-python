
from mjml.core import ComponentCategory

from ._base import BodyComponent


__all__ = ['MjRaw']


class MjRaw(BodyComponent):
    component_name = 'mj-raw'
    categories = frozenset({ComponentCategory.RAW})
    ending_tag = True

    rawElement = True

    @classmethod
    def allowed_attrs(cls):
        return {
            'position': 'enum(file-start)',
        }

    def render(self):
        return self.getContent()
