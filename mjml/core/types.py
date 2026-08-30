"""
Attribute types as declared in a component's "allowed_attrs()".

A type declaration like "unit(px,%){1,4}" describes which values a user may
write for that attribute. The types are ported from mjml but some matchers
are stricter, see below.
"""

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, ClassVar, Optional

from mjml.core._css_colors import CSS_COLOR_NAMES


__all__ = ['AttributeType', 'initialize_type']


def _js_str(value: Any) -> str:
    """
    Return the value as JavaScript would interpolate it into a string.

    Some attribute values are converted to booleans before validation, so
    Python's "True" would be confusing in an error message.
    """
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)


@dataclass(frozen=True)
class AttributeType:
    matchers: tuple[re.Pattern, ...] = ()
    error_template: Optional[str] = None
    type_name: ClassVar[str] = 'Type'

    def is_valid(self, value: Any) -> bool:
        str_value = _js_str(value)
        return any(matcher.search(str_value) for matcher in self.matchers)

    # js: getErrorMessage()
    def error_message(self, value: Any) -> Optional[str]:
        if self.is_valid(value):
            return None
        template = self.error_template
        if template is None:
            # Deviation: mjml JS emits a trailing space here.
            template = f'has invalid value: $value for type {self.type_name}'
        return template.replace('$value', _js_str(value))

    # js: getValue()
    def normalized_value(self, value: Any) -> Any:
        return value


@dataclass(frozen=True)
class BooleanType(AttributeType):
    type_name: ClassVar[str] = 'Boolean'

    def is_valid(self, value: Any) -> bool:
        # "true" and "false" are converted to booleans before validation
        return isinstance(value, bool)


_COLOR_SHORTHAND = re.compile(r'^#\w{3}$', re.ASCII)
_COLOR_SHORTHAND_PARTS = re.compile(r'^#(\w)(\w)(\w)$', re.ASCII)

_COLOR_MATCHERS = (
    # we don't want to accept "garbage rgb(1,2,3)" even though mjml JS
    # accepts that.
    re.compile(r'^rgba\(\d{1,3},\s?\d{1,3},\s?\d{1,3},\s?\d(\.\d{1,3})?\)$', re.IGNORECASE),
    re.compile(r'^rgb\(\d{1,3},\s?\d{1,3},\s?\d{1,3}\)$', re.IGNORECASE),
    re.compile(r'^#([0-9a-f]{3}){1,2}$', re.IGNORECASE),
    # color names are case-sensitive, unlike the hex notation above
    re.compile('^({})$'.format('|'.join(CSS_COLOR_NAMES))),
)


@dataclass(frozen=True)
class ColorType(AttributeType):
    matchers: tuple[re.Pattern, ...] = _COLOR_MATCHERS
    type_name: ClassVar[str] = 'Color'

    def normalized_value(self, value: Any) -> Any:
        # The same conversion is currently done by "formatAttributes()" which
        # can not use this module yet: some attributes are declared without a
        # type and "initialize_type()" has no type for an empty declaration.
        if isinstance(value, str) and _COLOR_SHORTHAND.match(value):
            return _COLOR_SHORTHAND_PARTS.sub(r'#\1\1\2\2\3\3', value)
        return value


@dataclass(frozen=True)
class EnumType(AttributeType):
    type_name: ClassVar[str] = 'Enum'


@dataclass(frozen=True)
class IntegerType(AttributeType):
    # anchored on purpose: mjml JS matches "\d+" so even "abc5" is an integer there
    matchers: tuple[re.Pattern, ...] = (re.compile(r'^\d+$'),)
    type_name: ClassVar[str] = 'Integer'


@dataclass(frozen=True)
class StringType(AttributeType):
    matchers: tuple[re.Pattern, ...] = (re.compile(r'.*'),)
    type_name: ClassVar[str] = 'String'


@dataclass(frozen=True)
class UnitType(AttributeType):
    type_name: ClassVar[str] = 'Unit'


def _params(type_config: str) -> list[str]:
    params_match = re.search(r'\(([^)]+)\)', type_config)
    if params_match is None:
        # mjml JS fails with a TypeError for a declaration like "enum()"
        raise ValueError(f'No parameters in {type_config}')
    return params_match.group(1).split(',')


def _enum_type(type_config: str) -> AttributeType:
    values = _params(type_config)
    accepted = ', '.join(value for value in values if value)
    if '' in values:
        accepted += ' or an empty value'
    return EnumType(
        matchers=tuple(re.compile('^%s$' % re.escape(value)) for value in values),
        error_template=(
            f'has invalid value: $value for type Enum, only accepts {accepted}'
        ),
    )


def _unit_type(type_config: str) -> AttributeType:
    units = _params(type_config)
    args_match = re.search(r'\{([^}]+)\}', type_config)
    # the number of values defaults to 1, e.g. "unit(px,%)" vs "unit(px,%){1,4}"
    args = args_match.group(1).split(',') if args_match else ['1']

    # We want to accept only real numbers even though mjml JS accepts something
    # like "1.2.3px"
    number = r'(?:\d+(?:\.\d+)?|\.\d+)'
    if type_config.startswith('unitWithNegative'):
        number = '-?' + number
    # "auto" is written without a number (like "0"), the empty unit in
    # "unit(px,%,)" allows bare numbers
    allow_auto = '|auto' if ('auto' in units) else ''
    unit_names = '|'.join(re.escape(unit) for unit in units if unit != 'auto')

    value_pattern = f'(?:{number}(?:{unit_names})|0{allow_auto}) ?'
    matcher = re.compile('^(?:%s){%s}$' % (value_pattern, ','.join(args)))
    accepted = '(%s) units' % ', '.join(unit for unit in units if unit)
    if '' in units:
        accepted += ' or a plain number,'
    nr_values = ' to '.join(args)
    value_word = 'value' if (nr_values == '1') else 'values'
    return UnitType(
        matchers=(matcher,),
        error_template=(
            f'has invalid value: $value for type Unit, '
            f'only accepts {accepted} and {nr_values} {value_word}'
        ),
    )


_TYPE_CONSTRUCTORS = (
    (re.compile(r'^boolean', re.IGNORECASE), lambda config: BooleanType()),
    (re.compile(r'^enum', re.IGNORECASE), _enum_type),
    (re.compile(r'^color', re.IGNORECASE), lambda config: ColorType()),
    (re.compile(r'^(unit|unitWithNegative)\(.*\)', re.IGNORECASE), _unit_type),
    (re.compile(r'^string', re.IGNORECASE), lambda config: StringType()),
    (re.compile(r'^integer', re.IGNORECASE), lambda config: IntegerType()),
)


@lru_cache(maxsize=None)
def initialize_type(type_config: str) -> AttributeType:
    """
    Return the AttributeType for a type declaration like "unit(px,%){1,4}".

    Raises a ValueError if there is no such type - an attribute declared
    without a type must not be passed to this function.
    """
    for matcher, type_constructor in _TYPE_CONSTRUCTORS:
        if matcher.match(type_config):
            return type_constructor(type_config)
    raise ValueError(f'No type found for {type_config}')
