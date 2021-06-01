
from io import BytesIO, StringIO
from pathlib import Path, PurePath

from lxml import etree as lxml_etree

from .core import initComponent
from .helpers import mergeOutlookConditionnals, json_to_xml, omit, skeleton_str as default_skeleton
from .lib import merge_dicts, AttrDict


def ignore_empty(values):
    result = []
    for value in values:
        if value:
            result.append(value)
    return tuple(result)


def mjml_to_html(xml_fp_or_json, skeleton=None, template_dir=None):
    if isinstance(xml_fp_or_json, dict):
        xml_fp = StringIO(json_to_xml(xml_fp_or_json))
    elif isinstance(xml_fp_or_json, str):
        xml_fp = StringIO(xml_fp_or_json)
    else:
        xml_fp = xml_fp_or_json

    if template_dir is None and hasattr(xml_fp, 'name'):
        template_dir = Path(xml_fp.name).parent

    mjml_doc = lxml_etree.parse(xml_fp)
    mjml_root = mjml_doc.xpath('/mjml')[0]

    skeleton_path = skeleton
    if skeleton_path:
        raise NotImplementedError('not yet implemented')
    skeleton = default_skeleton

    fonts = {
      'Open Sans': 'https://fonts.googleapis.com/css?family=Open+Sans:300,400,500,700',
      'Droid Sans': 'https://fonts.googleapis.com/css?family=Droid+Sans:300,400,500,700',
      'Lato': 'https://fonts.googleapis.com/css?family=Lato:300,400,500,700',
      'Roboto': 'https://fonts.googleapis.com/css?family=Roboto:300,400,500,700',
      'Ubuntu': 'https://fonts.googleapis.com/css?family=Ubuntu:300,400,500,700',
    }
    # LATER: ability to override fonts via **options

    globalDatas = AttrDict({
        'backgroundColor'    : None,
        'breakpoint'         : '480px',
        'classes'            : {},
        'classesDefault'     : {},
        'defaultAttributes'  : {},
        'fonts'              : fonts,
        'inlineStyle'        : [],
        'headStyle'          : {},
        'componentsHeadStyle': [],
        'headRaw'            : [],
        'mediaQueries'       : {},
        'preview'            : '',
        'style'              : [],
        'title'              : '',
    })

    validationLevel = 'skip'
    errors = []
    # LATER: optional validation

    mjBody = mjml_root.xpath('/mjml/mj-body')[0]
    mjHead = mjml_root.xpath('/mjml/mj-head')
    if mjHead:
        assert len(mjHead) == 1
        mjHead = mjHead[0]

    def processing(node, context, parseMJML=None):
        if node is None:
            return None
        # LATER: upstream passes "parseMJML=identity" for head components
        # but we can not process lxml nodes here. applyAttributes() seems to do
        # the right thing though...
        _mjml_data = parseMJML(node) if parseMJML else applyAttributes(node)
        initialDatas = merge_dicts(_mjml_data, {'context': context})
        node_tag = getattr(node, 'tag', None)
        component = initComponent(name=node_tag, **initialDatas)
        if not component:
            return None
        if hasattr(component, 'handler'):
            return component.handler()
        if hasattr(component, 'render'):
            return component.render()
        raise AssertionError('should not reach this')

    def applyAttributes(mjml_element):
        if len(mjml_element) == 0:
            return {}
        def parse(_mjml, parentMjClass='', *, template_dir):
            tagName = _mjml.tag
            is_comment = not isinstance(tagName, str)
            if is_comment:
                # XML comment: <cyfunction Comment at 0x…>
                # (this needs to be extended when "keepComments" should be implemented)
                return None
            attributes = _mjml.attrib
            children = [child for child in _mjml]
            classes = ignore_empty(attributes.get('mj-class', '').split(' '))

            # upstream parses text contents (+ comments) in mjml-parser-xml/index.js
            content = _mjml.text

            attributesClasses = {}
            for css_class in classes:
                mjClassValues = globalDatas.classes[css_class]
                attributesClasses.update(mjClassValues)

            parent_mj_classes = ignore_empty(parentMjClass.split(' '))
            def default_attr_classes(value):
                return globalDatas.classesDefault.get(value, {}).get(tagName, {})
            defaultAttributesForClasses = merge_dicts(*map(default_attr_classes, parent_mj_classes))
            nextParentMjClass = attributes.get('mj-class', parentMjClass)

            _attrs_omit = omit(attributes, 'mj-class')
            _returned_attributes = merge_dicts(
                globalDatas.defaultAttributes.get(tagName, {}),
                attributesClasses,
                defaultAttributesForClasses,
                _attrs_omit,
            )

            # XXX: ugly - but need raw XML content for mj-raw tag
            if tagName == 'mj-raw':
                from lxml.etree import tostring
                content = tostring(_mjml).strip().decode('utf-8')
                content = content.replace('<mj-raw>', '').replace('</mj-raw>', '')
            elif tagName == 'mj-include':
                mj_include_subtree = handle_include(attributes['path'], parse_mjml=parse, template_dir=template_dir)
                return mj_include_subtree
            result = {
                'tagName': tagName,
                'content': content,
                # see also https://stackoverflow.com/a/30986529/138526 for the
                # ".text"/".tail" difference
                'tail'   : _mjml.tail,

                'attributes': _returned_attributes,
                'globalAttributes': globalDatas.defaultAttributes.get('mj-all', {}).copy(),
                'children': [], # will be set afterwards
            }
            _parse_mjml = lambda mjml: parse(mjml, nextParentMjClass, template_dir=template_dir)
            for child_result in _map_to_tuple(children, _parse_mjml, filter_none=True):
                if isinstance(child_result, (tuple, list)):
                    result['children'].extend(child_result)
                else:
                    result['children'].append(child_result)
            return result

        return parse(mjml_element, template_dir=template_dir)

    def addHeadStyle(identifier, headStyle):
        globalDatas.headStyle[identifier] = headStyle

    def addMediaQuery(className, parsedWidth, unit):
        width_str = f'{parsedWidth}{unit}'
        globalDatas.mediaQueries[className] = f'{{ width:{width_str} !important; max-width: {width_str}; }}'

    def addComponentHeadSyle(headStyle):
        globalDatas.componentsHeadStyle.append(headStyle)

    def setBackgroundColor(color):
        globalDatas.backgroundColor = color

    bodyHelpers = AttrDict(
        addHeadStyle = addHeadStyle,
        addMediaQuery = addMediaQuery,
        addComponentHeadSyle = addComponentHeadSyle,
        setBackgroundColor = setBackgroundColor,
        backgroundColor = lambda node, context: processing(node, context, applyAttributes),
    )

    def _head_data_add(attr, *params):
        if attr not in globalDatas:
            param_str = ''.join(params) if isinstance(params, list) else params
            exc_msg = f'A mj-head element add an unknown head attribute : {attr} with params {param_str}'
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

    headHelpers = AttrDict(
        add = _head_data_add,
    )
    globalDatas.headRaw = processing(mjHead, headHelpers)
    content = processing(mjBody, bodyHelpers, applyAttributes)

    content = skeleton(
        content=content,
        # upstream just passes this extra key to skeleton() as JavaScript
        # won't complain about additional parameters.
        **omit(globalDatas, ('classesDefault',)),
    )
    # LATER: upstream has also beautify
    # LATER: upstream has also minify

    content = mergeOutlookConditionnals(content)

    return AttrDict({
        'html': content,
        'errors': errors,
    })


def _map_to_tuple(items, map_fn, filter_none=None):
    results = []
    for item in items:
        result = map_fn(item)
        if filter_none and (result is None):
            continue
        results.append(result)
    return tuple(results)


def handle_include(path_value, parse_mjml, *, template_dir):
    path = PurePath(path_value)
    if path.is_absolute():
        included_path = path
    elif template_dir:
        included_path = template_dir / path
    else:
        included_path = path
    # Upstream mjml does not raise an error if the included file was not found.
    # Instead they generate a HTML comment with a failure notice.
    # using plain "open()" call because "PurePath" does not support ".open()"
    with open(included_path, 'rb') as fp:
        included_bytes = fp.read()
    # Need to load the included file as binary - otherwise non-ascii characters
    # in utf8-encoded include files were messed up on Windows.
    # Not sure what happens if lxml needs to handle non-utf8 contents but it
    # works for me at least for utf8 now.
    if b'<mjml>' not in included_bytes:
        included_bytes = b'<mjml><mj-body>' + included_bytes + b'</mj-body></mjml>'
    # lxml does not like non-ascii StringIO input but utf8-encoded BytesIO works
    # seen with pypy3 7.3.1, lxml 4.6.3 (Fedora 34)
    fp_included = BytesIO(included_bytes)
    mjml_doc = lxml_etree.parse(fp_included)
    _body = mjml_doc.xpath('/mjml/mj-body')
    _head = mjml_doc.xpath('/mjml/mj-head')
    assert (not _head), '<mj-head> within <mj-include> not yet implemented '
    assert _body

    if _body:
        body_result = parse_mjml(_body[0], template_dir=included_path.parent)
        assert body_result['tagName'] == 'mj-body'
        included_items = body_result['children']
        return included_items
