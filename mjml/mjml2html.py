import dataclasses
from collections.abc import Callable, Mapping, Sequence
from io import BytesIO, StringIO
from pathlib import Path, PurePath
from typing import TYPE_CHECKING, Any, NamedTuple, Optional, TypeVar, Union

from bs4 import BeautifulSoup
from dotmap import DotMap

from mjml.core import initComponent
from mjml.core.registry import components_for_invocation
from mjml.elements.head._head_base import HeadComponent
from mjml.errors import (
    MJMLValidationErrors,
    Severity,
    ValidationError,
    ValidationLevel,
)
from mjml.helpers import (
    json_to_xml,
    mergeOutlookConditionals,
    omit,
    remove_important_from_inlined_styles,
    skeleton_str as default_skeleton,
)
from mjml.node import Node, NodeKind
from mjml.parser import parse_document
from mjml.validator import validate_tree


if TYPE_CHECKING:
    from _typeshed import StrPath, SupportsRead

    from mjml.core.api import Component, HandlerResult
    T = TypeVar("T")


class ParseResult(NamedTuple):
    html: str
    errors: Sequence[ValidationError]


FpOrJson = Union[Mapping[str, Any], str, bytes, "SupportsRead[str]", "SupportsRead[bytes]"]


class ParsedInput(NamedTuple):
    source: str
    template_dir: Optional["StrPath"]
    template_path: Optional[str]
    # a template built from JSON has no source the caller could look at
    from_json: bool


def parse_input(xml_fp_or_json: FpOrJson, template_dir: Optional["StrPath"]) -> ParsedInput:
    from_json = isinstance(xml_fp_or_json, Mapping)
    if isinstance(xml_fp_or_json, Mapping):
        xml_fp = StringIO(json_to_xml(xml_fp_or_json))
    elif isinstance(xml_fp_or_json, str):
        xml_fp = StringIO(xml_fp_or_json)
    elif isinstance(xml_fp_or_json, bytes):
        xml_fp = BytesIO(xml_fp_or_json)
    else:
        xml_fp = xml_fp_or_json

    template_path: Optional[str] = getattr(xml_fp, 'name', None)
    if (template_dir is None) and isinstance(template_path, (str, PurePath)):
        template_dir = Path(template_path).parent

    source = xml_fp.read()
    if isinstance(source, bytes):
        source = source.decode('utf8')
    return ParsedInput(source, template_dir, template_path, from_json)


def validate(
    xml_fp_or_json: FpOrJson,
    *,
    template_dir: Optional["StrPath"] = None,
    custom_components: Optional[Sequence[type["Component"]]] = None,
) -> Sequence[ValidationError]:
    components = components_for_invocation(custom_components)
    parsed = parse_input(xml_fp_or_json, template_dir)
    node_tree = _node_tree(parsed, components, report_include_errors=True)
    return _validation_errors(parsed, components, node_tree)


def _node_tree(
    parsed: ParsedInput,
    components: Any,
    report_include_errors: bool = False,
) -> Node:
    template_file = str(parsed.template_path) if parsed.template_path else None
    node_tree = parse_document(
        parsed.source,
        components,
        file=template_file,
        template_dir=parsed.template_dir,
        report_include_errors=report_include_errors,
    )
    if node_tree is None:
        if parsed.template_path:
            raise ValueError(f"Could not parse '{parsed.template_path}'")
        raise ValueError('Could not parse mjml input')
    return node_tree


def _validation_errors(
    parsed: ParsedInput,
    components: Any,
    node_tree: Node,
) -> list[ValidationError]:
    errors = validate_tree(node_tree, components)
    if parsed.from_json:
        # mjml xml was generated dynamically from json so error positions are meaningless
        # to the user.
        errors = [dataclasses.replace(error, line=None, column=None) for error in errors]
    return errors


def mjml_to_html(
    xml_fp_or_json: FpOrJson,
    skeleton: Optional[str] = None,
    template_dir: Optional["StrPath"] = None,
    custom_components: Optional[Sequence[type["Component"]]] = None,
    keep_comments: bool = True,
    printer_support: bool = False,
    validation_level: Union[str, ValidationLevel] = ValidationLevel.SKIP,
) -> ParseResult:
    components = components_for_invocation(custom_components)
    level = ValidationLevel(validation_level)

    parsed = parse_input(xml_fp_or_json, template_dir)
    template_dir = parsed.template_dir
    validation_errors: list[ValidationError] = []
    if level is not ValidationLevel.SKIP:
        # a validation run reports a broken include instead of stopping at it
        validation_errors = _validation_errors(
            parsed, components, _node_tree(parsed, components, True)
        )
        if level is ValidationLevel.STRICT:
            blocking = [e for e in validation_errors if e.severity is Severity.ERROR]
            if blocking:
                raise MJMLValidationErrors(blocking)

    mjml_root = _node_tree(parsed, components)

    skeleton_path = skeleton
    if skeleton_path:
        raise NotImplementedError('not yet implemented')
    skeleton_func = default_skeleton

    fonts = {
      'Open Sans': 'https://fonts.googleapis.com/css?family=Open+Sans:300,400,500,700',
      'Droid Sans': 'https://fonts.googleapis.com/css?family=Droid+Sans:300,400,500,700',
      'Lato': 'https://fonts.googleapis.com/css?family=Lato:300,400,500,700',
      'Roboto': 'https://fonts.googleapis.com/css?family=Roboto:300,400,500,700',
      'Ubuntu': 'https://fonts.googleapis.com/css?family=Ubuntu:300,400,500,700',
    }
    # LATER: ability to override fonts via **options

    mjml_lang = mjml_root.attributes.get('lang', 'und')
    mjml_dir = mjml_root.attributes.get('dir', 'auto')
    mjml_owa = mjml_root.attributes.get('owa', 'mobile')
    globalDatas: Mapping[str, Any] = DotMap({
        'breakpoint'         : '480px',
        'classes'            : {},
        'classesDefault'     : {},
        'defaultAttributes'  : {},
        'htmlAttributes'     : {},
        'fonts'              : fonts,
        'inlineStyle'        : [],
        'headStyle'          : {},
        'componentsHeadStyle': [],
        'headRaw'            : [],
        'lang'               : mjml_lang,
        'dir_'               : mjml_dir,
        'forceOWADesktop'    : (mjml_owa == 'desktop'),
        'printerSupport'     : printer_support,
        'mediaQueries'       : {},
        'preview'            : '',
        'style'              : [],
        'title'              : '',
    })

    errors: list[ValidationError] = validation_errors

    mjBody = _find_child(mjml_root, 'mj-body')
    if not mjBody:
        raise ValueError('Did not find <mj-body>!')
    mjHead = _find_child(mjml_root, 'mj-head')

    def processing(node: Optional[Any], context: dict[str, Any],
                   parseMJML: Optional[Callable[[Any], Any]]=None) -> "HandlerResult":
        if node is None:
            return None
        # LATER: upstream passes "parseMJML=identity" for head components
        # but we can not process lxml nodes here. applyAttributes() seems to do
        # the right thing though...
        _mjml_data = parseMJML(node) if parseMJML else applyAttributes(node)
        initialDatas = {**_mjml_data, 'context': context}
        node_tag = node.tag_name
        component = initComponent(name=node_tag, components=components, **initialDatas)
        if not component:
            return None
        if isinstance(component, HeadComponent):
            return component.handler()
        elif not hasattr(component, 'render'):
            raise AssertionError('component has no render() method')
        return component.render()

    def applyAttributes(node: Node) -> dict[str, Any]:
        def parse(node: Node, parentMjClass: str = '') -> Optional[dict[str, Any]]:
            if node.kind is NodeKind.COMMENT:
                if not keep_comments:
                    return None
                return {
                    'tagName': 'mj-raw',
                    'content': node.content,
                    'attributes': {},
                    'globalAttributes': {},
                    'children': [],
                }
            tagName = node.tag_name
            attributes = dict(node.attributes)
            mj_class = attributes.get('mj-class')
            # The parser converts "true"/"false" for mj-class to booleans.
            mj_class = mj_class if isinstance(mj_class, str) else None
            classes = ignore_empty(mj_class.split(' ')) if mj_class else ()

            attributesClasses = {}
            for css_class in classes:
                mjClassValues = globalDatas.get("classes").get(css_class)
                if mjClassValues:
                    multiple_classes = {}
                    if attributesClasses.get('css-class') and mjClassValues.get('css-class'):
                        multiple_classes['css-class'] = (
                            f"{attributesClasses['css-class']} {mjClassValues['css-class']}"
                        )
                    attributesClasses.update(mjClassValues)
                    attributesClasses.update(multiple_classes)

            parent_mj_classes = ignore_empty(parentMjClass.split(' '))

            def default_attr_classes(value: Any) -> Any:
                return globalDatas.get("classesDefault").get(value, {}).get(tagName, {})

            defaultAttributesForClasses = {}
            for parent_mj_class in parent_mj_classes:
                defaultAttributesForClasses |= default_attr_classes(parent_mj_class)
            nextParentMjClass = mj_class if (mj_class is not None) else parentMjClass

            _attrs_omit = omit(attributes, 'mj-class')
            _returned_attributes = {
                **globalDatas.get("defaultAttributes").get(tagName, {}),
                **attributesClasses,
                **defaultAttributesForClasses,
                **_attrs_omit,
            }

            children = []
            for child in node.children:
                child_result = parse(child, nextParentMjClass)
                if child_result is not None:
                    children.append(child_result)
            return {
                'tagName': tagName,
                'content': node.content,
                'attributes': _returned_attributes,
                'globalAttributes': globalDatas.get("defaultAttributes").get('mj-all', {}).copy(),
                'children': children,
            }

        return parse(node) or {}

    def addHeadStyle(identifier, headStyle):
        globalDatas["headStyle"][identifier] = headStyle

    def addMediaQuery(className, parsedWidth=None, unit=None, padding=None):
        rule = '{'
        if (parsedWidth is not None) and (unit is not None):
            width_str = f'{parsedWidth}{unit}'
            rule += f' width:{width_str} !important; max-width: {width_str};'
        if padding:
            rule += f' padding: {padding} !important;'
        rule += ' }'
        globalDatas["mediaQueries"][className] = rule

    def addComponentHeadSyle(headStyle):
        globalDatas["componentsHeadStyle"].append(headStyle)

    bodyHelpers = dict(
        components = components,
        addHeadStyle = addHeadStyle,
        addMediaQuery = addMediaQuery,
        addComponentHeadSyle = addComponentHeadSyle,
        processing = lambda node, context: processing(node, context, applyAttributes),
        globalData = globalDatas,
        lang = mjml_lang,
        dir_ = mjml_dir,
    )

    def _head_data_add(attr, *params):
        if attr not in globalDatas:
            param_str = ''.join(params) if isinstance(params, list) else params
            exc_msg = f'A mj-head element add an unknown head attribute: {attr} with params {param_str}' # noqa: E501
            raise ValueError(exc_msg)

        current_attr_value = globalDatas[attr]
        if isinstance(current_attr_value, (list, tuple)):
            current_attr_value.extend(params)
        elif len(params) == 1:
            assert len(params) == 1
            globalDatas[attr] = params[0]
        else:
            param_key, *param_values = params
            assert param_key not in current_attr_value, 'Not yet implemented'
            assert len(param_values) == 1, 'shortcut in implementation'
            current_attr_value[param_key] = param_values[0]

    headHelpers = dict(
        components = components,
        add = _head_data_add,
    )
    globalDatas["headRaw"] = processing(mjHead, headHelpers)
    content = processing(mjBody, bodyHelpers, applyAttributes)
    if not isinstance(content, str):
        # basically just a `None` check - only only head components might return a tuple
        raise ValueError('No <mj-body> content generated!')

    if attrs := globalDatas.get("htmlAttributes"):
        contentSoup = BeautifulSoup(content, 'html.parser')
        for selector, data in attrs.items():
            for attrName, value in data.items():
                for element in contentSoup.select(selector):
                    element[attrName] = value or ''

        content = contentSoup.decode_contents()

    content = skeleton_func(
        content=content,
        # upstream just passes this extra key to skeleton() as JavaScript
        # won't complain about additional parameters.
        **omit(globalDatas, ('classesDefault', 'htmlAttributes')),
    )
    # LATER: upstream has also beautify
    # LATER: upstream has also minify

    if len(globalDatas.get("inlineStyle")) > 0:
        try:
            import css_inline
        except ImportError:
            raise ImportError('CSS inlining is an optional feature. Run `pip install -e ".[css_inlining]"` to install the required dependencies.') # noqa: E501

        extra_css = ''.join(globalDatas.get("inlineStyle"))
        inliner = css_inline.CSSInliner(
            extra_css=extra_css,
            inline_style_tags=False,
            keep_link_tags=True,
            keep_style_tags=True,
            load_remote_stylesheets=False,
        )
        inlined_content = inliner.inline(content)
        # js: Juice drops "!important" while inlining ("preserveImportant" is
        # false by default) but "css_inline" has no such option.
        content = remove_important_from_inlined_styles(content, inlined_content)

    content = mergeOutlookConditionals(content)

    return ParseResult(
        html=content,
        errors=errors,
    )


def _find_child(parent: Node, tagName: str) -> Optional[Node]:
    # upstream uses lodash's find() which only searches direct children
    for child in parent.children:
        if child.tag_name == tagName:
            return child
    return None


def ignore_empty(values: Sequence[Optional["T"]]) -> Sequence["T"]:
    result: list["T"] = []
    for value in values:
        if value:
            result.append(value)
    return tuple(result)
