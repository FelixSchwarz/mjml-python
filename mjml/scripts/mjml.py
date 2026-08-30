#!/usr/bin/env python3
"""
mjml.

Usage:
  mjml --validate [--template-dir=<path>] <MJML-FILE>
  mjml [--template-dir=<path>] [--config.keepComments=False]
       [--validation-level=<level>] <MJML-FILE> [-o <OUTPUT-FILE>]

Options:
  --template-dir=<path>    base dir for mj-include (default: path of mjml file)
  --config.keepComments=False  whether comments in mjml should be present in the generated html (default: true)
  --validate               report problems in the template and generate no html, exits nonzero when something was found
  --validation-level=<level>  "skip" (default), "soft" to report problems and generate html anyway or "strict" to refuse rendering
"""
# ruff: noqa: E501

import sys
from collections.abc import Collection
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Optional, Union

from docopt import DocoptExit, docopt

from mjml.errors import MJMLValidationErrors, ValidationError, ValidationLevel
from mjml.mjml2html import mjml_to_html, validate


def main(argv: Optional[list[str]] = None) -> None:
    try:
        command = _parse_command(argv)
    except (DocoptExit, _ArgumentError) as error:
        sys.stderr.write(f'{error}\n')
        sys.exit(1)

    validate_only = isinstance(command, ValidateCommand)
    if validate_only:
        exit_code = _run_validation(command)
    else:
        exit_code = _run_render(command)

    if exit_code:
        sys.exit(exit_code)


@dataclass(frozen=True)
class ValidateCommand:
    input_filename: str
    template_dir: Optional[str]


@dataclass(frozen=True)
class RenderCommand:
    input_filename: str
    output_filename: Optional[str]
    template_dir: Optional[str]
    keep_comments: bool
    validation_level: ValidationLevel


Command = Union[ValidateCommand, RenderCommand]


class _ArgumentError(ValueError):
    pass


def _parse_command(argv: Optional[list[str]]) -> Command:
    arguments = docopt(__doc__, argv=argv)

    if arguments['--validate']:
        return ValidateCommand(
            input_filename=arguments['<MJML-FILE>'],
            template_dir=arguments['--template-dir'],
        )

    keep_comments = _parse_bool(arguments['--config.keepComments'], default=True)
    if keep_comments is None:
        raise _ArgumentError(
            'value for --config.keepComments should be either true or false'
        )

    level_str = arguments['--validation-level'] or ValidationLevel.SKIP.value
    try:
        validation_level = ValidationLevel(level_str)
    except ValueError:
        levels = ', '.join(level.value for level in ValidationLevel)
        raise _ArgumentError(
            f'unknown validation level "{level_str}", use one of {levels}'
        ) from None

    return RenderCommand(
        input_filename=arguments['<MJML-FILE>'],
        output_filename=arguments['<OUTPUT-FILE>'],
        template_dir=arguments['--template-dir'],
        keep_comments=keep_comments,
        validation_level=validation_level,
    )


def _run_validation(command: ValidateCommand) -> int:
    with _open_input(command.input_filename) as mjml_fp:
        errors = validate(mjml_fp, template_dir=command.template_dir)

    _report(errors)
    return 1 if errors else 0


def _run_render(command: RenderCommand) -> int:
    try:
        with _open_input(command.input_filename) as mjml_fp:
            result = mjml_to_html(
                mjml_fp,
                template_dir=command.template_dir,
                keep_comments=command.keep_comments,
                validation_level=command.validation_level,
            )
    except MJMLValidationErrors as validation_error:
        _report(validation_error.errors)
        return 1

    _report(result.errors)
    _write_html(result.html, command.output_filename)
    return 0


def _open_input(mjml_filename: str) -> BinaryIO:
    if mjml_filename == '-':
        return BytesIO(sys.stdin.buffer.read())

    # the file name is used for "mj-include" and in the reported problems
    return Path(mjml_filename).open('rb')


def _write_html(html: str, output_filename: Optional[str]) -> None:
    if output_filename:
        with Path(output_filename).open('w') as html_fp:
            html_fp.write(html)
        return

    # Always return binary data encoded as UTF-8 to avoid encoding problems on
    # Windows, whose default encoding may not represent all generated content.
    sys.stdout.buffer.write(html.encode('utf8'))


def _report(errors: Collection[ValidationError]) -> None:
    # write errors to stderr so they are separated from rendering output on stdout
    for error in errors:
        sys.stderr.write(error.formatted_message() + '\n')


def _parse_bool(value: Union[str, None], *, default: bool) -> Union[bool, None]:
    if value is None:
        return default
    truthy = {'true', '1', 'yes', 'y'}
    falsey = {'false', '0', 'no', 'n'}

    value_lower = value.strip().lower()
    if value_lower in truthy:
        return True
    elif value_lower in falsey:
        return False
    else:
        return None


if __name__ == '__main__':
    main()
