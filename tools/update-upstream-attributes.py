#!/usr/bin/env python3
"""
usage: update-upstream-attributes.py [-h] UPSTREAM_DIR

Script to update "tests/upstream_attributes.json" with the attributes declared
by the mjml reference implementation (NodeJS). UPSTREAM_DIR is a checkout of
the mjml sources, the JavaScript does not have to be built.

positional arguments:
  UPSTREAM_DIR
"""

import argparse
import json
import re
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple


SNAPSHOT_PATH = Path(__file__).parent.parent / 'tests' / 'upstream_attributes.json'

_class_re = re.compile(r'class\s+(\w+)\s+extends\s+([\w.]+)\s*\{')
_component_name_re = re.compile(r"static\s+componentName\s*=\s*'([^']+)'")
_allowed_attrs_re = re.compile(r'static\s+allowedAttributes\s*=\s*')
_spread_re = re.compile(r'\.\.\.(\w+)\.allowedAttributes')
_attr_re = re.compile(r"(?:'([^']+)'|([\w-]+))\s*:\s*'([^']*)'")
_ending_tag_re = re.compile(r'static\s+endingTag\s*=\s*true')


class JsClass(NamedTuple):
    component_name: str
    attrs: dict[str, str]
    ending_tag: bool
    extends: str
    # "mj-wrapper" declares "...MjSection.allowedAttributes"
    inherits_from: list[str]


def parse_upstream(upstream_dir: Path) -> dict[str, JsClass]:
    js_files = sorted(upstream_dir.glob('packages/mjml-*/src/*.js'))
    if not js_files:
        raise SystemExit(f'no components found in {upstream_dir}/packages/mjml-*/src/')

    classes: dict[str, JsClass] = {}
    num_components = 0
    for js_file in js_files:
        source = js_file.read_text(encoding='utf8')
        num_components += len(_component_name_re.findall(source))
        for class_name, js_class in _parse_classes(source):
            classes[class_name] = js_class
    if len(classes) != num_components:
        raise SystemExit(
            f'parsed {len(classes)} components but found {num_components} '
            'component names - the JavaScript syntax likely changed'
        )
    return {
        js_class.component_name: js_class._replace(
            attrs=_with_inherited_attrs(class_name, classes),
            ending_tag=_ending_tag(class_name, classes),
        )
        for class_name, js_class in classes.items()
    }


def _parse_classes(source: str) -> Iterator[tuple[str, JsClass]]:
    class_matches = list(_class_re.finditer(source))
    for i, class_match in enumerate(class_matches):
        is_last = (i + 1) == len(class_matches)
        end = len(source) if is_last else class_matches[i + 1].start()
        body = source[class_match.end():end]

        name_match = _component_name_re.search(body)
        if name_match is None:
            continue
        attrs_match = _allowed_attrs_re.search(body)
        declaration = _object_literal(body, attrs_match.end()) if attrs_match else ''
        attrs = {
            (attr.group(1) or attr.group(2)): attr.group(3)
            for attr in _attr_re.finditer(declaration)
        }
        js_class = JsClass(
            component_name=name_match.group(1),
            attrs=attrs,
            ending_tag=bool(_ending_tag_re.search(body)),
            extends=class_match.group(2),
            inherits_from=_spread_re.findall(declaration),
        )
        yield class_match.group(1), js_class


def _object_literal(source: str, start: int) -> str:
    depth = 0
    for i in range(start, len(source)):
        if source[i] == '{':
            depth += 1
        elif source[i] == '}':
            depth -= 1
            if depth == 0:
                return source[start:i]
    raise SystemExit('unterminated "allowedAttributes" declaration')


def _with_inherited_attrs(class_name: str, classes: dict[str, JsClass]) -> dict[str, str]:
    js_class = classes[class_name]
    attrs = {}
    for inherited in js_class.inherits_from:
        if inherited not in classes:
            raise SystemExit(f'{class_name} inherits attributes from unknown {inherited}')
        attrs.update(_with_inherited_attrs(inherited, classes))
    attrs.update(js_class.attrs)
    return attrs


def _ending_tag(class_name: str, classes: dict[str, JsClass]) -> bool:
    # JavaScript classes inherit static attributes ("MjWrapper extends MjSection")
    js_class = classes[class_name]
    if js_class.ending_tag:
        return True
    parent = js_class.extends
    return _ending_tag(parent, classes) if (parent in classes) else False


def upstream_version(upstream_dir: Path) -> str:
    package_json = json.loads((upstream_dir / 'packages' / 'mjml' / 'package.json').read_text())
    return package_json['version']


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('upstream_dir', metavar='UPSTREAM_DIR', type=Path)
    args = parser.parse_args()

    components = parse_upstream(args.upstream_dir)
    snapshot = {
        'mjml_version': upstream_version(args.upstream_dir),
        'allowed_attributes': {name: c.attrs for name, c in sorted(components.items())},
        'ending_tags': sorted(name for name, c in components.items() if c.ending_tag),
    }
    previous = {}
    if SNAPSHOT_PATH.exists():
        previous = json.loads(SNAPSHOT_PATH.read_text(encoding='utf8'))
    SNAPSHOT_PATH.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + '\n', encoding='utf8')

    num_attrs = sum(len(c.attrs) for c in components.values())
    num_ending_tags = len(snapshot['ending_tags'])
    print(
        f'mjml {snapshot["mjml_version"]}: {len(components)} components, '
        f'{num_attrs} attributes, {num_ending_tags} ending tags'
    )
    for line in _changes(previous.get('allowed_attributes', {}), snapshot['allowed_attributes']):
        print(line)


def _changes(before: dict, after: dict) -> Iterator[str]:
    for name in sorted(set(before) | set(after)):
        old, new = before.get(name, {}), after.get(name, {})
        for attr in sorted(set(old) - set(new)):
            yield f'  removed  {name} {attr} = {old[attr]!r}'
        for attr in sorted(set(new) - set(old)):
            yield f'  added    {name} {attr} = {new[attr]!r}'
        for attr in sorted(set(old) & set(new)):
            if old[attr] != new[attr]:
                yield f'  changed  {name} {attr}: {old[attr]!r} -> {new[attr]!r}'


if __name__ == '__main__':
    sys.exit(main())
