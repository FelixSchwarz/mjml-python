from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING, NamedTuple, Optional

from mjml.core.api import GLOBAL_ATTRS, ComponentCategory
from mjml.core.types import initialize_type
from mjml.errors import ValidationError, ValidationRule
from mjml.node import Node, NodeKind


if TYPE_CHECKING:
    from mjml.core.api import Component


__all__ = ['RULES']

# tags without a component of their own which are valid all the same
COMPONENTLESS_TAGS = frozenset({'mj-all', 'mj-class', 'mj-selector', 'mj-html-attribute'})

Components = Mapping[str, type["Component"]]


class _Declaration(NamedTuple):
    destination: tuple[str, str]
    description: str
    node: Node


# Declarations whose renderer destination is selected by an attribute.
# Each key is (container tag, declaration tag), and each value is
# (head-data collection, key attribute). Other non-empty children of mj-attributes
# use their element name as the destination key.
ATTRIBUTE_KEYED_DECLARATIONS = {
    ('mj-head', 'mj-font'): ('fonts', 'name'),
    ('mj-attributes', 'mj-class'): ('classes', 'name'),
    ('mj-html-attributes', 'mj-selector'): ('htmlAttributes', 'path'),
}

# Containers whose child elements define head-data declarations.
DECLARATION_CONTAINERS = frozenset({
    'mj-attributes',
    'mj-html-attributes',
})

# Attributes which we do not support yet.
# These will be accepted by `valid_attributes` so the specialized check for
# `report_unsupported_features` can build a more helpful error message.
UNSUPPORTED_ATTRS = {
    ('mj-raw', 'position'): 'position is not implemented by this port (#74)',
}


def _error(node: Node, message: str, rule: ValidationRule) -> ValidationError:
    return ValidationError(
        message=message,
        tag_name=node.tag_name,
        rule=rule,
        line=node.line,
        column=node.column,
        file=node.file,
        included_in=node.included_in,
    )


def valid_tag(node: Node, components: Components) -> Iterator[ValidationError]:
    if (node.tag_name in COMPONENTLESS_TAGS) or (node.tag_name in components):
        return
    message = f"Element {node.tag_name} doesn't exist or is not registered"
    yield _error(node, message, ValidationRule.VALID_TAG)


def valid_attributes(node: Node, components: Components) -> Iterator[ValidationError]:
    component_cls = components.get(node.tag_name)
    if component_cls is None:
        return
    allowed = set(component_cls.allowed_attrs()) | GLOBAL_ATTRS
    unknown = [
        attr for attr in node.attributes
        if (attr not in allowed) and ((node.tag_name, attr) not in UNSUPPORTED_ATTRS)
    ]
    if not unknown:
        return
    if len(unknown) == 1:
        message = f'Attribute {unknown[0]} is illegal'
    else:
        message = f'Attributes {", ".join(unknown)} are illegal'
    yield _error(node, message, ValidationRule.VALID_ATTRIBUTES)


def valid_types(node: Node, components: Components) -> Iterator[ValidationError]:
    component_cls = components.get(node.tag_name)
    if component_cls is None:
        return
    declared_types = component_cls.allowed_attrs()
    for attr, value in node.attributes.items():
        type_declaration = declared_types.get(attr)
        if not type_declaration:
            continue
        error_message = initialize_type(type_declaration).error_message(value)
        if error_message is not None:
            message = f'Attribute {attr} {error_message}'
            yield _error(node, message, ValidationRule.VALID_TYPES)


def valid_children(node: Node, components: Components) -> Iterator[ValidationError]:
    component_cls = components.get(node.tag_name)
    if component_cls is None:
        return
    accepts = component_cls.accepts
    if ComponentCategory.ANY in accepts:
        return
    for child in node.children:
        if child.kind is NodeKind.COMMENT:
            continue
        child_cls = components.get(child.tag_name)
        # an unknown element is "valid_tag"'s business, not ours
        if child_cls is None:
            continue
        if (child.tag_name in accepts) or (child_cls.categories & accepts):
            continue
        message = f'{child.tag_name} cannot be used inside {node.tag_name}'
        parents = _possible_parents(child.tag_name, components)
        if parents:
            message += f', only inside: {", ".join(parents)}'
        yield _error(child, message, ValidationRule.VALID_CHILDREN)


def include_errors(node: Node, components: Components) -> Iterator[ValidationError]:
    yield from node.errors


def report_unsupported_features(node: Node, components: Components) -> Iterator[ValidationError]:
    for attr in node.attributes:
        message = UNSUPPORTED_ATTRS.get((node.tag_name, attr))
        if message:
            yield _error(node, message, ValidationRule.NOT_IMPLEMENTED)

    if node.tag_name == 'mj-head':
        yield from _colliding_declarations(node)


def _colliding_declarations(head: Node) -> Iterator[ValidationError]:
    """Report declarations that target the same renderer destination."""
    seen: set[tuple[str, str]] = set()

    for declaration in _head_declarations(head):
        if declaration.destination in seen:
            message = f'{declaration.description} is declared more than once.'
            yield _error(declaration.node, message, ValidationRule.NOT_IMPLEMENTED)
        seen.add(declaration.destination)


def _head_declarations(head: Node) -> Iterator[_Declaration]:
    for parent in (head, *_declaration_containers(head)):
        for child in parent.children:
            if child.kind is NodeKind.COMMENT:
                continue

            declaration = _declaration(parent.tag_name, child)
            if declaration is not None:
                yield declaration


def _declaration_containers(head: Node) -> Iterator[Node]:
    for child in head.children:
        if child.tag_name in DECLARATION_CONTAINERS:
            yield child


def _declaration(parent_tag: str, node: Node) -> Optional[_Declaration]:
    destination_and_key_attribute = ATTRIBUTE_KEYED_DECLARATIONS.get(
        (parent_tag, node.tag_name)
    )
    if destination_and_key_attribute is not None:
        destination, key_attribute = destination_and_key_attribute
        key_value = node.attributes.get(key_attribute)
        if not isinstance(key_value, str):
            # a declaration without its key never gets that far
            return None

        return _Declaration(
            destination=(destination, key_value),
            description=f'{node.tag_name} {key_attribute}="{key_value}"',
            node=node,
        )

    if parent_tag != 'mj-attributes':
        return None

    # The renderer ignores empty declarations, so they occupy no destination.
    if not node.attributes:
        return None

    return _Declaration(
        destination=('defaultAttributes', node.tag_name),
        description=node.tag_name,
        node=node,
    )


def _possible_parents(tag_name: str, components: Components) -> list[str]:
    child_cls = components[tag_name]
    return sorted(
        name
        for name, component_cls in components.items()
        if (ComponentCategory.ANY in component_cls.accepts)
        or (tag_name in component_cls.accepts)
        or (child_cls.categories & component_cls.accepts)
    )


RULES = (
    valid_tag,
    valid_attributes,
    valid_types,
    valid_children,
    include_errors,
    report_unsupported_features,
)
