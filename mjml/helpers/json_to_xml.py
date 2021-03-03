"""Convert MJML from JSON format to XML."""

from typing import Any, Mapping


def json_to_xml(root: Mapping[str, Any], indent: str = '') -> str:
    attr_dict = dict(root.get('attributes', {}), id=root.get('id'))
    attributes = []
    for key, value in attr_dict.items():
        if isinstance(value, str):
            attributes.append(f'{key}="{value}"')
    attributes_str = (' ' if attributes else '') + ' '.join(attributes)

    if root.get('content'):
        content = f'{indent}  {root.get("content")}'
    elif 'children' in root:
        child_indent = f'{indent}  '
        children = []
        for child in root.get('children', []):
            if child.get('attributes', {}).get('passport', {}).get('hidden'):
                continue
            child_xml = json_to_xml(child, indent=child_indent)
            children.append(child_xml)
        content = '\n'.join(children)
    else:
        content = ''

    return f'{indent}<{root["tagName"]}{attributes_str}>\n{content}\n{indent}</{root["tagName"]}>'
