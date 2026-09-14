"""
Builds the node tree from the mjml source.

The content of an ending tag is copied out of the source verbatim rather than
serialized back from a parsed tree. There is no decoding step, so there is no
encoding step which could forget to escape again - escaped input stays escaped.
"""

import dataclasses
import re
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from mjml.errors import Include, Severity, ValidationError, ValidationRule
from mjml.helpers import (
    CircularIncludeError,
    IncludeAccess,
    IncludeDenial,
    IncludePolicy,
    convertBooleansOnAttrs,
    guard_against_circular_include,
    include_access,
    include_source,
    is_regular_file,
    read_include_file,
    resolve_include,
)
from mjml.node import Node, NodeKind


if TYPE_CHECKING:
    from _typeshed import StrPath

    from mjml.core.api import Component


__all__ = ['parse_document']

_Attrs = list  # list[tuple[str, Optional[str]]] as "html.parser" hands them over

# "mjml" is the default and the only one which is parsed as a template
INCLUDE_TYPES = frozenset({'mjml', 'css', 'html'})

# an attribute name, optionally followed by its value
_ATTR_RE = re.compile(r"""([^\s=/>]+)\s*(?:=\s*(?:"[^"]*"|'[^']*'|[^\s"'=<>`]*))?""")


def parse_document(
    source: str,
    components: Mapping[str, type["Component"]],
    *,
    file: Optional[str] = None,
    template_dir: Optional["StrPath"] = None,
    includes: Optional[IncludePolicy] = None,
    include_policy_events: Optional[list[ValidationError]] = None,
) -> Optional[Node]:
    """
    The <mjml> element of "source", or `None` when there is none.

    An include which cannot be used does not stop the parsing. Its place is
    taken by a node which carries the problem as a validation error, so a
    single tree serves both the validation and the rendering. Most problems
    still let the caller decide whether the tree may be rendered; one which
    dropped part of the mail does not, regardless of validation level.

    Without "includes" every "mj-include" is such a node: the element is
    dropped, as mjml js does, and reported. With a policy, the directories it
    allows are fixed here for the whole tree: a nested include resolves its
    path against the file which contains it, but may not reach further than the
    top-level template could.
    """
    ending_tags = frozenset(
        name for name, component in components.items() if component.ending_tag
    )
    if includes is None:
        scope = None
    elif not template_dir:
        # mjml js falls back to the working directory, but for a server process
        # that is an accident of the deployment rather than a decision of the caller
        raise ValueError(
            'a template which was not read from a file needs "template_dir" for includes'
        )
    else:
        scope = _IncludeScope(access=include_access(includes), base_dir=template_dir)
    if include_policy_events is None:
        include_policy_events = []
    origin = _Origin(
        ending_tags=ending_tags,
        file=file,
        includes=scope,
        included_in = (),
        include_chain = (),
        included_heads = [],
        css_includes = [],
        include_policy_events=include_policy_events,
    )
    return _parse(source, origin)


@dataclass(frozen=True)
class _IncludeScope:
    """The directories an include may read from, and where its path starts."""
    access: IncludeAccess
    # where a relative include path starts
    base_dir: "StrPath"


@dataclass(frozen=True)
class _Origin:
    """The file being parsed and the includes which led to it."""
    ending_tags: frozenset
    file: Optional[str]
    includes: Optional[_IncludeScope]
    included_in: Sequence[Include]
    include_chain: Sequence[Path]
    # <mj-head> of every included file, collected for the document's own head
    included_heads: list
    css_includes: list
    # Unlike nodes, this collection survives include expansion and discarded markup.
    include_policy_events: list[ValidationError]


def _parse(source: str, origin: _Origin) -> Optional[Node]:
    builder = _NodeParser(source, origin)
    builder.feed(source)
    builder.close()
    root = builder.root
    head_children = (*origin.included_heads, *origin.css_includes)
    if (root is None) or not head_children:
        return root
    return _with_included_heads(root, head_children)


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
        attributes = _attributes(raw, tag_name, attrs)
        # mjml js handles includes before boolean conversion, so filesystem
        # names such as "true" and "false" remain strings.
        if tag_name != 'mj-include':
            attributes = convertBooleansOnAttrs(attributes)
        return _Element(
            tag_name=tag_name,
            attributes=attributes,
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
        names = [name for name, _ in attrs]
    attributes: dict = {}
    for written, (_, value) in zip(names, attrs):
        # behave like the js implementation: a repeated attribute keeps the value
        # it was written with first, and a valueless attribute is an empty
        # string rather than None
        attributes.setdefault(written, value or '')
    return attributes


def _included_nodes(element: _Element, origin: _Origin) -> Iterator[Node]:
    """The nodes an "mj-include" stands for, or one node carrying the error."""
    scope = origin.includes
    if scope is None:
        # nothing about the include is looked at, not even its path
        msg = 'mj-include is disabled and the element was ignored, pass "includes=IncludePolicy(roots=...)" to enable includes'  # noqa: E501
        yield _failed_include(
            element,
            origin,
            message=msg,
            rule=ValidationRule.INCLUDE_DISABLED,
            tag_name='mj-include',
        )
        return
    path_value = element.attributes.get('path')
    if not path_value:
        yield _failed_include(element, origin, 'mj-include has no "path" attribute')
        return
    include_type = element.attributes.get('type')
    if include_type and (include_type not in INCLUDE_TYPES):
        # MJML js treats an unknown type silently as "mjml", and unlike every other
        # failure here, the include still expands normally: nothing is dropped
        known_include_types = ', '.join(sorted(INCLUDE_TYPES))
        _msg = f'unknown mj-include type "{include_type}", use one of {known_include_types}'
        yield _failed_include(element, origin, _msg, content_dropping=False)
        include_type = None

    resolved = resolve_include(path_value, template_dir=scope.base_dir, access=scope.access)
    if isinstance(resolved, IncludeDenial):
        # js: this comment stands in for the include, nothing is reported
        yield _failed_include(
            element,
            origin,
            f'mj-include "{path_value}" was denied: {resolved.reason}',
            content='<!-- mj-include denied -->',
            rule=ValidationRule.INCLUDE_DENIED,
            tag_name='mj-include',
        )
        return
    if not is_regular_file(resolved):
        message = f'the included file "{path_value}" ({resolved}) is not a regular file'
        comment = f'<!-- mj-include fails to read file : {path_value} at {resolved} -->'
        yield _failed_include(element, origin, message, content=comment)
        return
    try:
        if include_type in ('css', 'html'):
            # only an mjml include is wrapped when the file has no <mjml>
            source = read_include_file(resolved)
        else:
            source = include_source(resolved)
    except (OSError, UnicodeDecodeError) as error:
        # js: mjml renders this comment in place of the include
        comment = f'<!-- mj-include fails to read file : {path_value} at {resolved} -->'
        if isinstance(error, UnicodeDecodeError):
            message = f'could not decode the included file "{path_value}" ({resolved}) as UTF-8'
        else:
            message = f'could not read the included file "{path_value}" ({resolved})'
        yield _failed_include(
            element,
            origin,
            message,
            content=comment,
        )
        return

    if include_type == 'css':
        # js: an included stylesheet becomes an <mj-style> at the end of the
        # head, wherever in the document the include stands
        is_inline = element.attributes.get('css-inline') == 'inline'
        attributes = {'inline': 'inline'} if is_inline else {}
        origin.css_includes.append(Node(
            tag_name='mj-style',
            attributes=attributes,
            content=source,
            line=element.line,
            column=element.column,
            file=origin.file,
            included_in=tuple(origin.included_in),
        ))
        return
    if include_type == 'html':
        yield _raw_node(element, origin, source)
        return

    try:
        include_chain = guard_against_circular_include(resolved, origin.include_chain)
    except CircularIncludeError as cycle:
        yield _failed_include(element, origin, str(cycle))
        return
    included_origin = _Origin(
        ending_tags=origin.ending_tags,
        file=str(resolved),
        includes=dataclasses.replace(scope, base_dir=resolved.parent),
        included_in=(*origin.included_in, Include(file=origin.file, line=element.line)),
        include_chain=include_chain,
        included_heads=[],
        css_includes=[],
        include_policy_events=origin.include_policy_events,
    )
    included_root = _parse(source, included_origin)
    if included_root is None:
        message = f'the included file "{path_value}" ({resolved}) contains no mjml'
        yield _failed_include(element, origin, message)
        return
    # js: findTag() stops at the first match, so a second head or body in an
    # included file is not looked at
    included_head = _first_child(included_root, 'mj-head')
    included_body = _first_child(included_root, 'mj-body')
    if included_head is not None:
        # the head of an included file belongs to the document's head, wherever
        # in the document the include stands
        origin.included_heads.extend(included_head.children)
    if included_body is not None:
        yield from included_body.children


def _first_child(node: Node, tag_name: str) -> Optional[Node]:
    for child in node.children:
        if child.tag_name == tag_name:
            return child
    return None


def _failed_include(
    element: _Element,
    origin: _Origin,
    message: str,
    content: str = '',
    rule: ValidationRule = ValidationRule.INCLUDE_ERROR,
    severity: Severity = Severity.ERROR,
    tag_name: str = 'mj-raw',
    content_dropping: bool = True,
) -> Node:
    error = ValidationError(
        message=message,
        tag_name=tag_name,
        rule=rule,
        severity=severity,
        line=element.line,
        column=element.column,
        file=origin.file,
        included_in=tuple(origin.included_in),
    )
    if content_dropping:
        # collected regardless of validation level: a dropped part of the mail
        # must never depend on whether the caller happened to validate
        origin.include_policy_events.append(error)
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


def _with_included_heads(root: Node, head_children: tuple) -> Node:
    """Put the head elements of the included files into the document's head."""
    children = list(root.children)
    for index, child in enumerate(children):
        if child.tag_name == 'mj-head':
            children[index] = dataclasses.replace(
                child, children=(*child.children, *head_children)
            )
            break
    else:
        # a document which has no head of its own gets one
        children.insert(0, Node(tag_name='mj-head', children=head_children, file=root.file))
    return dataclasses.replace(root, children=tuple(children))
