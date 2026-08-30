from collections.abc import Iterator, Mapping
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any, Optional

from bs4 import Comment, NavigableString

from mjml.errors import Include, ValidationError, ValidationRule
from mjml.helpers import (
    convertBooleansOnAttrs,
    parse_include_document,
    read_include_file,
    resolve_include_path,
)
from mjml.node import Node, NodeKind


if TYPE_CHECKING:
    from _typeshed import StrPath

    from mjml.core.api import Component


__all__ = ['ending_tag_names', 'node_tree_from_soup']


@dataclass(frozen=True)
class _Source:
    """The file currently being read and the includes which led to it."""
    ending_tags: frozenset
    file: Optional[str]
    template_dir: Optional["StrPath"]
    included_in: tuple[Include, ...]


def ending_tag_names(components: Mapping[str, type["Component"]]) -> frozenset:
    return frozenset(name for name, component in components.items() if component.ending_tag)


def node_tree_from_soup(
    mjml_root: Any,
    components: Mapping[str, type["Component"]],
    *,
    file: Optional[str] = None,
    template_dir: Optional["StrPath"] = None,
) -> Node:
    source = _Source(ending_tag_names(components), file, template_dir, ())
    return _element_node(mjml_root, source)


def _element_node(tag: Any, source: _Source) -> Node:
    if tag.name in source.ending_tags:
        # everything below an ending tag is markup for the mail, not mjml
        children: tuple[Node, ...] = ()
        content = tag.decode_contents()
    else:
        children = tuple(_child_nodes(tag, source))
        content = _text_content(tag)
    return Node(
        tag_name=tag.name,
        attributes=convertBooleansOnAttrs(tag.attrs),
        children=children,
        content=content,
        line=tag.sourceline,
        column=tag.sourcepos,
        file=source.file,
        included_in=source.included_in,
    )


def _child_nodes(tag: Any, source: _Source) -> Iterator[Node]:
    for child in tag.children:
        if isinstance(child, Comment):
            # BeautifulSoup tracks no source position for strings
            yield Node(
                tag_name='',
                kind=NodeKind.COMMENT,
                content=f'<!--{child}-->',
                file=source.file,
                included_in=source.included_in,
            )
        elif isinstance(child, NavigableString):
            pass
        elif child.name == 'mj-include':
            yield from _included_nodes(child, source)
        else:
            yield _element_node(child, source)


def _included_nodes(tag: Any, source: _Source) -> Iterator[Node]:
    path_value = tag.attrs.get('path')
    if path_value is None:
        yield _failed_include_node(tag, 'mj-include has no "path" attribute', source)
        return
    include_type = tag.attrs.get('type')
    resolved = resolve_include_path(path_value, template_dir=source.template_dir)
    try:
        if include_type in ('css', 'html'):
            content = read_include_file(path_value, template_dir=source.template_dir)
        else:
            included_doc = parse_include_document(path_value, template_dir=source.template_dir)
    except OSError:
        # js: mjml renders this comment in place of the include
        comment = f'<!-- mj-include fails to read file : {path_value} at {resolved} -->'
        yield _failed_include_node(
            tag,
            f'could not read the included file "{path_value}" ({resolved})',
            source,
            content=comment,
        )
        return

    if include_type == 'css':
        # upstream turns this into an <mj-style> at the end of <mj-head>
        return
    if include_type == 'html':
        yield _raw_node(tag, content, source)
        return

    included_root = included_doc.mjml
    if included_root is None:
        yield _failed_include_node(
            tag,
            f'the included file "{path_value}" ({resolved}) contains no mjml',
            source,
        )
        return
    included_body = _direct_child(included_root, 'mj-body')
    if included_body is None:
        # <mj-head> of an included file is merged into the document head while
        # rendering, which happens outside this tree
        return
    included_source = replace(
        source,
        file=str(resolved),
        template_dir=resolved.parent,
        included_in=source.included_in + (Include(file=source.file, line=tag.sourceline),),
    )
    yield from _child_nodes(included_body, included_source)


def _failed_include_node(
    tag: Any,
    message: str,
    source: _Source,
    content: str = '',
) -> Node:
    """
    An include which produced nothing usable. It never resolves to no node at
    all: an include that goes wrong has to be visible to the caller.
    """
    error = ValidationError(
        message=message,
        tag_name='mj-raw',
        rule=ValidationRule.INCLUDE_ERROR,
        line=tag.sourceline,
        column=tag.sourcepos,
        file=source.file,
        included_in=source.included_in,
    )
    return _raw_node(tag, content, source, errors=(error,))


def _raw_node(
    tag: Any,
    content: str,
    source: _Source,
    errors: tuple[ValidationError, ...] = (),
) -> Node:
    return Node(
        tag_name='mj-raw',
        content=content,
        line=tag.sourceline,
        column=tag.sourcepos,
        file=source.file,
        included_in=source.included_in,
        errors=errors,
    )


def _direct_child(tag: Any, tag_name: str) -> Any:
    for child in tag.children:
        if getattr(child, 'name', None) == tag_name:
            return child
    return None


def _text_content(tag: Any) -> str:
    texts = [
        str(child).strip()
        for child in tag.children
        if isinstance(child, NavigableString) and not isinstance(child, Comment)
    ]
    return ''.join(text for text in texts if text)
