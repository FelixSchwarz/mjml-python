#!/usr/bin/env python3
"""
usage: update-upstream-validation.py [-h] [--mjml MJML]

Script to update "tests/upstream_validation.json" with the findings the mjml
reference implementation (NodeJS) reports for the templates in
"tests/invalid_templates/". Set the MJML environment variable (or --mjml) to
the mjml executable, as for "update-expected-html.py".
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


TEMPLATE_DIR = Path(__file__).parent.parent / 'tests' / 'invalid_templates'
SNAPSHOT_PATH = Path(__file__).parent.parent / 'tests' / 'upstream_validation.json'

# "Line 4 of /path/to.mjml (mj-text) - Attribute nope is illegal"
_finding_re = re.compile(r'^Line (\d+) of (.+?) \(([\w-]+)\) . (.*)$')

_ILLEGAL_ATTRS_RE = re.compile(r'^Attributes? ([\w, -]+?) (?:is|are) illegal$')
_INVALID_VALUE_RE = re.compile(r'^Attribute ([\w-]+) has invalid value:')
_UNKNOWN_ELEMENT_RE = re.compile(r"^Element [\w-]+ doesn't exist")
_BAD_CHILD_RE = re.compile(r'^[\w-]+ cannot be used inside ')


def classify(message: str) -> list[tuple[str, Optional[str]]]:
    """
    The rule and attribute a message is about.

    The messages themselves are not compared: this port words several of them
    differently on purpose.
    """
    match = _ILLEGAL_ATTRS_RE.match(message)
    if match:
        return [('valid-attributes', attr) for attr in match.group(1).split(', ')]
    match = _INVALID_VALUE_RE.match(message)
    if match:
        return [('valid-types', match.group(1))]
    if _UNKNOWN_ELEMENT_RE.match(message):
        return [('valid-tag', None)]
    if _BAD_CHILD_RE.match(message):
        return [('valid-children', None)]
    raise SystemExit(f'cannot classify upstream message: {message!r}')


def findings_for(mjml_js: str, template: Path) -> list[list]:
    process = subprocess.run(
        [mjml_js, str(template), '-s', '--validationLevel=strict'],
        capture_output=True, text=True, check=False,
    )
    findings = []
    for line in process.stderr.splitlines():
        line = line.strip()
        if (not line) or line.startswith('No matching component for tag'):
            # mjml writes this for an unknown head element and reports it as a
            # validation error as well
            continue
        match = _finding_re.match(line)
        if not match:
            raise SystemExit(f'unexpected output for {template.name}: {line!r}')
        tag_name = match.group(3)
        for rule, attribute in classify(match.group(4).strip()):
            findings.append([tag_name, rule, attribute])
    return sorted(findings)


def detect_mjml_js(argument: Optional[str]) -> str:
    if argument:
        return argument
    if 'MJML' in os.environ:
        return os.environ['MJML']
    raise SystemExit('unable to detect mjml executable, use env variable MJML')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mjml', default=None)
    args = parser.parse_args()
    mjml_js = detect_mjml_js(args.mjml)

    snapshot = {
        template.stem: findings_for(mjml_js, template)
        for template in sorted(TEMPLATE_DIR.glob('*.mjml'))
    }
    if not snapshot:
        raise SystemExit(f'no templates in {TEMPLATE_DIR}')
    SNAPSHOT_PATH.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + '\n', encoding='utf8')

    num_findings = sum(len(f) for f in snapshot.values())
    sys.stdout.write(f'{len(snapshot)} templates, {num_findings} findings\n')


if __name__ == '__main__':
    main()
