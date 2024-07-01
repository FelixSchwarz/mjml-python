import typing as t

import typing_extensions as te

from ._head_base import HeadComponent


__all__ = ['MjHtmlAttributes']

class MjHtmlAttributes(HeadComponent):
    component_name: t.ClassVar[str] = 'mj-html-attributes'

    @te.override
    def handler(self) -> None:
        add = self.context['add']
        _children = self.props.get("children")

        for child in _children:
            tagName = child['tagName']
            attributes = child['attributes']
            children = child['children']
            if tagName == 'mj-selector':
                path = attributes['path']

                custom = {}
                for c in children:
                    is_mj_html_attribute = (c['tagName'] == 'mj-html-attribute')
                    has_name = bool(c.get('attributes', {}).get('name', None))
                    if is_mj_html_attribute and has_name:
                        custom[c['attributes']['name']] = c['content']

                add('htmlAttributes', path, custom)
