

import re


__all__ = ['buildFontsTags']

def buildFontsTags(content, inlineStyle, fonts=None):
    toImport = []
    re_flags = re.IGNORECASE | re.MULTILINE
    for (name, url) in (fonts or {}).items():
        regex = re.compile(f'"[^"]*font-family:[^"]*{name}[^"]*"', re_flags)
        # double } ("}}") used for escaping
        inlineRegex = re.compile(f'font-family:[^;}}]*{name}', re_flags)
        # any(map(...)): any of "inlineStyle matches the inlineRegex
        if regex.search(content) or any(map(lambda s: inlineRegex.search(s), inlineStyle)):
            toImport.append(url)
    if not toImport:
        return ''

    link_builder = lambda url: f'<link href="{url}" rel="stylesheet" type="text/css">'
    link_tags_str = '\n'.join(map(link_builder, toImport))
    import_builder = lambda url: f'@import url({url});'
    import_lines_str = '\n'.join(map(import_builder, toImport))
    return f'''
      <!--[if !mso]><!-->
        {link_tags_str}
        <style type="text/css">
          {import_lines_str}
        </style>
      <!--<![endif]-->\n
    '''

