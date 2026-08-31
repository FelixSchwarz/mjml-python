"""
Builds the node tree from the mjml source.

The content of an ending tag is copied out of the source verbatim rather than
serialized back from a parsed tree. There is no decoding step, so there is no
encoding step which could forget to escape again - escaped input stays escaped.
"""

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import TYPE_CHECKING, Optional

from mjml.helpers import convertBooleansOnAttrs
from mjml.node import Node, NodeKind


if TYPE_CHECKING:
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
) -> Optional[Node]:
    """The <mjml> element of "source", or None when there is none."""
    ending_tags = frozenset(
        name for name, component in components.items() if component.ending_tag
    )
    builder = _NodeParser(source, ending_tags, file)
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

    def as_node(self, file: Optional[str]) -> Node:
        return Node(
            tag_name=self.tag_name,
            attributes=self.attributes,
            children=tuple(self.children),
            content=self.content,
            line=self.line,
            column=self.column,
            file=file,
        )


class _NodeParser(HTMLParser):
    def __init__(self, source: str, ending_tags: frozenset, file: Optional[str]) -> None:
        # entity references have to arrive as they were written
        super().__init__(convert_charrefs=False)
        self._source = source
        self._ending_tags = ending_tags
        self._file = file
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
        self._open[-1].children.append(
            Node(tag_name='', kind=NodeKind.COMMENT, content=f'<!--{data}-->',
                 line=self.getpos()[0], column=self.getpos()[1], file=self._file)
        )

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
        node = element.as_node(self._file)
        if self._open:
            self._open[-1].children.append(node)
        elif node.tag_name == 'mjml':
            self.root = node

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
