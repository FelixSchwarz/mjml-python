"""
Builds the node tree from the mjml source.

The content of an ending tag is copied out of the source verbatim rather than
serialized back from a parsed tree. There is no decoding step, so there is no
encoding step which could forget to escape again - escaped input stays escaped.
"""

import re
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from mjml.errors import Include, ValidationError, ValidationRule
from mjml.helpers import (
    CircularIncludeError,
    convertBooleansOnAttrs,
    guard_against_circular_include,
    include_source,
    resolve_include_path,
)
from mjml.node import Node, NodeKind


if TYPE_CHECKING:
    from _typeshed import StrPath

    from mjml.core.api import Component


__all__ = ['parse_document']

_Attrs = list  # list[tuple[str, Optional[str]]] as "html.parser" hands them over

# an attribute name, optionally followed by its value
_ATTR_RE = re.compile(r"""([^\s=/>]+)\s*(?:=\s*(?:"[^"]*"|'[^']*'|[^\s"'=<>`]*))?""")


def parse_document(
    source: str,
    components: Mapping[str, type["Component"]],
    *,
    file: Optional[str] = None,
    template_dir: Optional["StrPath"] = None,
) -> Optional[Node]:
    """The <mjml> element of "source", or None when there is none."""
    ending_tags = frozenset(
        name for name, component in components.items() if component.ending_tag
    )
    return _parse(source, _Origin(ending_tags, file, template_dir, (), ()))


@dataclass(frozen=True)
class _Origin:
    """The file being parsed and the includes which led to it."""
    ending_tags: frozenset
    file: Optional[str]
    template_dir: Optional["StrPath"]
    included_in: Sequence[Include]
    include_chain: Sequence[Path]


def _parse(source: str, origin: _Origin) -> Optional[Node]:
    builder = _NodeParser(source, origin)
    builder.feed(source)
    builder.close()
    return builder.root


@dataclass
class _Element:
    tag_name: str
    attributes: dict
    line: int
    column: int
    children: list = field(default_factory=list)
    content: str = ''

    def as_node(self, origin: "_Origin", errors: tuple = ()) -> Node:
        return Node(
            tag_name=self.tag_name,
            attributes=self.attributes,
            children=tuple(self.children),
            content=self.content,
            line=self.line,
            column=self.column,
            file=origin.file,
            included_in=tuple(origin.included_in),
            errors=errors,
        )


class _NodeParser(HTMLParser):
    def __init__(self, source: str, origin: "_Origin") -> None:
        # entity references have to arrive as they were written
        super().__init__(convert_charrefs=False)
        self._source = source
        self._origin = origin
        self._ending_tags = origin.ending_tags
        self._file = origin.file
        self._line_offsets = _line_offsets(source)
        self._open: list[_Element] = []
        self.root: Optional[Node] = None
        # Open ending tags, so a stray closing tag cannot end opaque content.
        self._ending_open: list[str] = []
        self._content_start = 0

    # --- markup ---

    def handle_starttag(self, tag: str, attrs: _Attrs) -> None:
        if self._ending_open:
            if tag in self._ending_tags:
                self._ending_open.append(tag)
            return
        raw = self.get_starttag_text() or ''
        self._open.append(self._element(tag, attrs, raw))
        if tag in self._ending_tags:
            self._ending_open.append(tag)
            self._content_start = self._offset() + len(raw)

    def handle_startendtag(self, tag: str, attrs: _Attrs) -> None:
        if self._ending_open:
            return
        element = self._element(tag, attrs, self.get_starttag_text() or '')
        self._finish(element)

    def handle_endtag(self, tag: str) -> None:
        if self._ending_open:
            if tag not in self._ending_open:
                return
            while self._ending_open.pop() != tag:
                pass
            if self._ending_open:
                return
            content = self._source[self._content_start:self._offset()]
            self._open[-1].content = content.strip()
        if not self._open:
            return
        # a stray closing tag must not pop an element it does not belong to
        if not any(element.tag_name == tag for element in self._open):
            return
        while self._open:
            element = self._open.pop()
            self._finish(element)
            if element.tag_name == tag:
                return

    def handle_comment(self, data: str) -> None:
        if self._ending_open or not self._open:
            return
        line, column = self.getpos()
        comment_node = Node(
            tag_name='',
            kind=NodeKind.COMMENT,
            content=f'<!--{data}-->',
            line=line,
            column=column,
            file=self._file,
            included_in=tuple(self._origin.included_in),
        )
        self._open[-1].children.append(comment_node)

    # --- text ---

    def handle_data(self, data: str) -> None:
        self._add_text(data)

    def handle_entityref(self, name: str) -> None:
        self._add_text(f'&{name};')

    def handle_charref(self, name: str) -> None:
        self._add_text(f'&#{name};')

    # --- helpers ---

    def _add_text(self, text: str) -> None:
        if self._ending_open or not self._open or not text.strip():
            return
        current = self._open[-1]
        current.content = f'{current.content}{text.strip()}'.strip()

    def _element(self, tag_name: str, attrs: _Attrs, raw: str) -> _Element:
        line, column = self.getpos()
        return _Element(
            tag_name=tag_name,
            attributes=convertBooleansOnAttrs(_attributes(raw, tag_name, attrs)),
            line=line,
            column=column,
        )

    def _finish(self, element: _Element) -> None:
        if element.tag_name == 'mj-include':
            nodes = tuple(_included_nodes(element, self._origin))
        else:
            nodes = (element.as_node(self._origin),)
        if self._open:
            self._open[-1].children.extend(nodes)
        elif nodes and nodes[0].tag_name == 'mjml':
            self.root = nodes[0]

    def _offset(self) -> int:
        line, column = self.getpos()
        return self._line_offsets[line - 1] + column

    def close(self) -> None:
        super().close()
        # an unclosed element still belongs in the tree
        while self._open:
            self._finish(self._open.pop())


def _line_offsets(source: str) -> list:
    offsets = [0]
    for index, character in enumerate(source):
        if character == '\n':
            offsets.append(index + 1)
    return offsets


def _attributes(raw: str, tag_name: str, attrs: _Attrs) -> dict:
    """
    The attributes with their names as they were written.

    "html.parser" lower-cases attribute names while mjml keeps them, and an
    attribute is only known by the name the component declares.
    """
    names = _ATTR_RE.findall(raw[1 + len(tag_name):].rstrip('>').rstrip('/'))
    if len(names) != len(attrs):
        # the fallback keeps a surprising start tag from losing attributes
        return {name: value or '' for name, value in attrs}
    # a valueless attribute is an empty string, not None
    return {written: value or '' for written, (_, value) in zip(names, attrs)}


def _included_nodes(element: _Element, origin: _Origin) -> Iterator[Node]:
    """The nodes an "mj-include" stands for, or one node carrying the error."""
    path_value = element.attributes.get('path')
    if not path_value:
        yield _failed_include(element, origin, 'mj-include has no "path" attribute')
        return
    include_type = element.attributes.get('type')
    resolved = resolve_include_path(path_value, template_dir=origin.template_dir)
    try:
        source = include_source(path_value, template_dir=origin.template_dir)
    except OSError:
        # js: mjml renders this comment in place of the include
        comment = f'<!-- mj-include fails to read file : {path_value} at {resolved} -->'
        yield _failed_include(
            element,
            origin,
            f'could not read the included file "{path_value}" ({resolved})',
            content=comment,
        )
        return

    if include_type == 'css':
        # upstream turns this into an <mj-style> at the end of <mj-head>
        return
    if include_type == 'html':
        yield _raw_node(element, origin, source)
        return

    try:
        include_chain = guard_against_circular_include(resolved, origin.include_chain)
    except CircularIncludeError as cycle:
        yield _failed_include(element, origin, str(cycle))
        return
    origin = _Origin(
        ending_tags=origin.ending_tags,
        file=str(resolved),
        template_dir=resolved.parent,
        included_in=(*origin.included_in, Include(file=origin.file, line=element.line)),
        include_chain=include_chain,
    )
    included_root = _parse(source, origin)
    if included_root is None:
        yield _failed_include(
            element, origin, f'the included file "{path_value}" ({resolved}) contains no mjml'
        )
        return
    for child in included_root.children:
        # <mj-head> of an included file is merged elsewhere
        if child.tag_name == 'mj-body':
            yield from child.children


def _failed_include(
    element: _Element,
    origin: _Origin,
    message: str,
    content: str = '',
    rule: ValidationRule = ValidationRule.INCLUDE_ERROR,
) -> Node:
    error = ValidationError(
        message=message,
        tag_name='mj-raw',
        rule=rule,
        line=element.line,
        column=element.column,
        file=origin.file,
        included_in=tuple(origin.included_in),
    )
    return _raw_node(element, origin, content, errors=(error,))


def _raw_node(element: _Element, origin: _Origin, content: str, errors: tuple = ()) -> Node:
    replacement = _Element(
        tag_name='mj-raw',
        attributes={},
        line=element.line,
        column=element.column,
        content=content,
    )
    return replacement.as_node(origin, errors=errors)
