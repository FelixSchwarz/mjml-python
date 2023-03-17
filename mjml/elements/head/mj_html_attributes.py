
from ._head_base import HeadComponent


__all__ = ['MjHtmlAttributes']

class MjHtmlAttributes(HeadComponent):
    component_name = 'mj-html-attributes'

    def handler(self):
        add = self.context['add']
        _children = self.props.children

        for child in _children:
            tagName = child['tagName']
            attributes = child['attributes']
            children = child['children']
            if tagName == 'mj-selector':
                path = attributes['path']

                custom = {}
                for c in children:
                    if c['tagName'] == 'mj-html-attribute' and bool(c.get('attributes', {}).get('name', None)): # noqa: E501
                        custom[c['attributes']['name']] = c['content']

                add('htmlAttributes', path, custom)
