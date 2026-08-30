from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING, Any, Optional

from bs4 import Comment, NavigableString

from .helpers import convertBooleansOnAttrs
from .node import Node, NodeKind


if TYPE_CHECKING:
    from mjml.core.api import Component


__all__ = ['ending_tag_names', 'node_tree_from_soup']


def ending_tag_names(components: Mapping[str, type["Component"]]) -> frozenset:
    return frozenset(name for name, component in components.items() if component.ending_tag)


def node_tree_from_soup(
    mjml_root: Any,
    components: Mapping[str, type["Component"]],
    file: Optional[str] = None,
) -> Node:
    return _element_node(mjml_root, ending_tag_names(components), file)


def _element_node(tag: Any, ending_tags: frozenset, file: Optional[str]) -> Node:
    if tag.name in ending_tags:
        # everything below an ending tag is markup for the mail, not mjml
        children: tuple[Node, ...] = ()
        content = tag.decode_contents()
    else:
        children = tuple(_child_nodes(tag, ending_tags, file))
        content = _text_content(tag)
    return Node(
        tag_name=tag.name,
        attributes=convertBooleansOnAttrs(tag.attrs),
        children=children,
        content=content,
        line=tag.sourceline,
        column=tag.sourcepos,
        file=file,
    )


def _child_nodes(tag: Any, ending_tags: frozenset, file: Optional[str]) -> Iterator[Node]:
    for child in tag.children:
        if isinstance(child, Comment):
            # BeautifulSoup tracks no source position for strings
            yield Node(tag_name='', kind=NodeKind.COMMENT, content=f'<!--{child}-->', file=file)
        elif not isinstance(child, NavigableString):
            yield _element_node(child, ending_tags, file)


def _text_content(tag: Any) -> str:
    texts = [
        str(child).strip()
        for child in tag.children
        if isinstance(child, NavigableString) and not isinstance(child, Comment)
    ]
    return ''.join(text for text in texts if text)
