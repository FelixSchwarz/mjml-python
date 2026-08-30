from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING

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
    unknown = [attr for attr in node.attributes if attr not in allowed]
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
)
