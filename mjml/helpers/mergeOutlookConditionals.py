
import re

__all__ = ['mergeOutlookConditionnals']

# OPTIMIZE ME: — check if previous conditionnal is `<!--[if mso | I`]>` too
def mergeOutlookConditionnals(content):
    # re.sub() replaces all occurrences by default ("g" modifier in JavaScript)
    return re.sub('(<!\[endif]-->\s*?<!--\[if mso \| IE]>)', '', content, re.MULTILINE)

