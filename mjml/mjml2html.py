
from lxml import etree as lxml_etree

from .core import initComponent
from .helpers import mergeOutlookConditionnals, omit, skeleton_str as default_skeleton
from .lib import merge_dicts, AttrDict


def ignore_empty(values):
    result = []
    for value in values:
        if value:
            result.append(value)
    return tuple(result)


def mjml_to_html(xml_fp, skeleton=None):
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
        'defaultAttributes'  : {},
        'fonts'              : fonts,
        'inlineStyle'        : [],
        'headStyle'          : {},
        'componentsHeadStyle': [],
        'headRaw'            : [],
        'mediaQueries'       : {},
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
        if (node is None) or (len(node) == 0):
            return None
        # LATER: upstream passes "parseMJML=identity" for head components
        # but we can not process lxml nodes here. applyAttributes() seems to do
        # the right thing though...
        _mjml_data = parseMJML(node) if parseMJML else applyAttributes(node)
        initialDatas = merge_dicts(_mjml_data, {'context': context})
        component = initComponent(name=node.tag, **initialDatas)
        if not component:
            return None
        if hasattr(component, 'handler'):
            return component.handler()
        if hasattr(component, 'render'):
            return component.render()
        raise AssertionError('should not reach this')

    def applyAttributes(mjml_element):
        def parse(_mjml, parentMjClass=''):
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
            def default_attr_classes(acc, value):
                _v = globalDatas.classesDefault.get(value, {}).get(tagName, {})
                return merge_dicts(acc, _v)
            defaultAttributesForClasses = merge_dicts(*map(default_attr_classes, parent_mj_classes))
            nextParentMjClass = attributes.get('mj-class', parentMjClass)

            _attrs_omit = omit(attributes, 'mj-class')
            _returned_attributes = merge_dicts(
                globalDatas.defaultAttributes.get(tagName, {}),
                attributesClasses,
                defaultAttributesForClasses,
                _attrs_omit,
            )
            result = {
                'tagName': tagName,
                'content': content,
                # see also https://stackoverflow.com/a/30986529/138526 for the
                # ".text"/".tail" difference
                'tail'   : _mjml.tail,

                'attributes': _returned_attributes,
                'globalAttributes': globalDatas.defaultAttributes.get('mj-all', {}).copy(),
                'children': tuple(map(lambda mjml: parse(mjml, nextParentMjClass), children)),
            }
            return result
        return parse(mjml_element)

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
            exc_msg = f'An mj-head element add an unkown head attribute : {attr} with params {param_str}'
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
        **globalDatas,
    )
    # LATER: upstream has also beautify
    # LATER: upstream has also minify

    content = mergeOutlookConditionnals(content)

    return AttrDict({
        'html': content,
        'errors': errors,
    })

