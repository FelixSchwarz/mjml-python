

__all__ = [
    'conditionalTag',
    'msoConditionalTag',
]

startConditionalTag = '<!--[if mso | IE]>'
startMsoConditionalTag = '<!--[if mso]>'
endConditionalTag = '<![endif]-->'
startNegationConditionalTag = '<!--[if !mso | IE]><!-->'
startMsoNegationConditionalTag = '<!--[if !mso><!-->'
endNegationConditionalTag = '<!--<![endif]-->'


def conditionalTag(content, negation=False):
    if negation:
        start, end = startNegationConditionalTag, endNegationConditionalTag
    else:
        start, end = startConditionalTag, endConditionalTag
    return start + content + end


def msoConditionalTag(content, negation=False):
    if negation:
        start, end = startMsoNegationConditionalTag, endNegationConditionalTag
    else:
        start, end = startConditionalTag, endConditionalTag
    return start + content + end

