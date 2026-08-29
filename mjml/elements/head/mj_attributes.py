from typing import ClassVar

from typing_extensions import override

from mjml.helpers import omit

from ._head_base import HeadComponent


__all__ = ['MjAttributes']


class MjAttributes(HeadComponent):
    component_name: ClassVar[str] = 'mj-attributes'

    @override
    def handler(self) -> None:
        add = self.context['add']
        if (_children := self.props.get("children")) is None:
            return None

        for child in _children:
            tagName = child['tagName']
            attributes = child['attributes']
            children = child['children']
            if tagName == 'mj-class':
                attr_name = attributes['name']
                add('classes', attr_name, omit(attributes, 'name'))

                class_defaults = {}
                for grand_child in children:
                    class_defaults[grand_child['tagName']] = grand_child['attributes']
                add('classesDefault', attr_name, class_defaults)
            else:
                if not attributes:
                    # TODO: not present upstream
                    continue
                add('defaultAttributes', tagName, attributes)
