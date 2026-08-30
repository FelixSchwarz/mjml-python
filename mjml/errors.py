from dataclasses import dataclass
from enum import Enum
from typing import Optional


__all__ = ['Include', 'Severity', 'ValidationError', 'ValidationRule']


class Severity(Enum):
    ERROR = 'error'
    WARNING = 'warning'


class ValidationRule(Enum):
    VALID_TAG = 'valid-tag'
    VALID_ATTRIBUTES = 'valid-attributes'
    VALID_TYPES = 'valid-types'
    VALID_CHILDREN = 'valid-children'
    INCLUDE_ERROR = 'include-error'


@dataclass(frozen=True)
class Include:
    file: Optional[str]
    line: Optional[int]


def _include_location(include: Include) -> str:
    if include.line is None:
        return f'file {include.file}'
    return f'line {include.line} of file {include.file}'


@dataclass(frozen=True)
class ValidationError:
    message: str
    tag_name: str
    rule: ValidationRule
    severity: Severity = Severity.ERROR
    line: Optional[int] = None
    column: Optional[int] = None
    file: Optional[str] = None
    # outermost include first, as the chain was walked
    included_in: tuple[Include, ...] = ()

    def formatted_message(self) -> str:
        if self.line is not None:
            location = f'Line {self.line}' + (f' of {self.file}' if self.file else '')
        elif self.file is not None:
            location = f'File {self.file}'
        else:
            location = ''
        if self.included_in:
            chain = ', itself included at '.join(
                _include_location(include) for include in reversed(self.included_in)
            )
            location += f', included at {chain}' if location else f'Included at {chain}'
        prefix = f'{location} ' if location else ''
        return f'{prefix}({self.tag_name}) - {self.message}'
