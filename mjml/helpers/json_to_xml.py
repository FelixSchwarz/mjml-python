"""Convert MJML from JSON format to XML."""

from typing import Any, Mapping


def json_to_xml(root: Mapping[str, Any], indent: str = '') -> str:
    attributes = ' '.join(
        f'{key}="{value}"'
        for key, value in dict(root.get('attributes', {}), id=root.get('id')).items()
        if isinstance(value, str)
    )
    if attributes:
        attributes = ' ' + attributes

    if root.get('content'):
        content = f'{indent}  {root.get("content")}'
    elif 'children' in root:
        child_indent = f'{indent}  '
        children = '\n'.join(
            json_to_xml(child, indent=child_indent)
            for child in root.get('children', [])
            if not child.get('attributes', {}).get('passport', {}).get('hidden')
        )
        content = children
    else:
        content = ''
        # return f'{indent}<{root["tagName"]}{attributes} />'

    return f'{indent}<{root["tagName"]}{attributes}>\n{content}\n{indent}</{root["tagName"]}>'
