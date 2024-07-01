import typing as t

import typing_extensions as te

from mjml.helpers import omit

from ._head_base import HeadComponent


__all__ = ['MjAttributes']


class MjAttributes(HeadComponent):
    component_name: t.ClassVar[str] = 'mj-attributes'

    @te.override
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

                assert not children, 'not yet implemented'
                # upstream:
                #   reduce(
                #     children,
                #     (acc, { tagName, attributes }) => ({
                #       ...acc,
                #       [tagName]: attributes,
                #     }),
                #     {},
                #   ),
                #def reducer(acc, tn_attr):
                #    tagName, attributes = tn_attr
                #    return {'tagName': attributes, **acc}
                #add('classesDefault', attr_name, reduce(children, reducer, {}))
            else:
                if not attributes:
                    # TODO: not present upstream
                    continue
                add('defaultAttributes', tagName, attributes)
