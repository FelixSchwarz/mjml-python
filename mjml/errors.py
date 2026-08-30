from dataclasses import dataclass
from enum import Enum
from typing import Optional


__all__ = ['Severity', 'ValidationError', 'ValidationRule']


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
class ValidationError:
    message: str
    tag_name: str
    rule: ValidationRule
    severity: Severity = Severity.ERROR
    line: Optional[int] = None
    column: Optional[int] = None
    file: Optional[str] = None

    def formatted_message(self) -> str:
        if self.line is not None:
            location = f'Line {self.line}' + (f' of {self.file}' if self.file else '')
        elif self.file is not None:
            location = f'File {self.file}'
        else:
            location = ''
        prefix = f'{location} ' if location else ''
        return f'{prefix}({self.tag_name}) - {self.message}'
