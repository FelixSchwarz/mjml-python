
from ._head_base import HeadComponent
from mjml.helpers import omit


__all__ = ['MjAttributes']

class MjAttributes(HeadComponent):
    def handler(self):
        add = self.context['add']
        _children = self.props.children

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

