from collections.abc import Mapping
from typing import TYPE_CHECKING

from mjml.errors import ValidationError
from mjml.node import Node, NodeKind

from .rules import RULES


if TYPE_CHECKING:
    from mjml.core.api import Component


__all__ = ['validate_tree']

# js: the root element is not validated, so a misplaced child of <mjml> is
# never reported - "validChildren" is a rule which runs on the parent.
SKIP_TAGS = frozenset({'mjml'})


def validate_tree(
    node: Node,
    components: Mapping[str, type["Component"]],
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    _validate_node(node, components, errors)
    return errors


def _validate_node(
    node: Node,
    components: Mapping[str, type["Component"]],
    errors: list[ValidationError],
) -> None:
    if node.kind is NodeKind.COMMENT:
        return
    if node.tag_name not in SKIP_TAGS:
        for rule in RULES:
            errors.extend(rule(node, components))
    for child in node.children:
        _validate_node(child, components, errors)
