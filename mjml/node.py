from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union


__all__ = ['Node', 'NodeKind']


class NodeKind(Enum):
    ELEMENT = 'element'
    COMMENT = 'comment'


@dataclass(frozen=True)
class Node:
    tag_name: str
    kind: NodeKind = NodeKind.ELEMENT
    attributes: Mapping[str, Union[str, bool]] = field(default_factory=dict)
    children: tuple['Node', ...] = ()
    # inner source of an ending tag, text content otherwise
    content: str = ''
    line: Optional[int] = None
    column: Optional[int] = None
    file: Optional[str] = None
