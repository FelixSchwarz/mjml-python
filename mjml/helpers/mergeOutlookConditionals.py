
import re


__all__ = ['mergeOutlookConditionals']

# OPTIMIZE ME: — check if previous conditional is `<!--[if mso | I`]>` too
def mergeOutlookConditionals(content):
    # re.sub() replaces all occurrences by default ("g" modifier in JavaScript)
    return re.sub(r'(<!\[endif]-->\s*?<!--\[if mso \| IE]>)', '', content, flags=re.MULTILINE)
