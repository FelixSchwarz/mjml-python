

__all__ = ['buildMediaQueriesTags']

def buildMediaQueriesTags(breakpoint, mediaQueries=None, forceOWADesktop=False,
                          printerSupport=False):
    if not mediaQueries:
        return ''
    elif hasattr(mediaQueries, 'items'):
        # dict
        mediaQueries = tuple(mediaQueries.items())

    def groupMediaQueries(prefix=''):
        # Upstream merges all class names which share the very same rule into a
        # single comma-separated selector list. Without gutters every rule is
        # unique (the class name is derived from the width) so this never
        # kicked in - gutter paddings however are identical for all "inner"
        # columns of a section.
        grouped: dict[str, list[str]] = {}
        for className, mediaQuery in mediaQueries:
            grouped.setdefault(mediaQuery, []).append(f'{prefix}.{className}')
        return '\n'.join(
            f'{", ".join(selectors)} {mediaQuery}'
            for mediaQuery, selectors in grouped.items()
        )

    media_queries_str = groupMediaQueries()
    thunderbird_media_queries_str = groupMediaQueries('.moz-text-html ')

    if printerSupport:
        printer_style = f'''<style type="text/css">
      @media only print {{
          {media_queries_str}
      }}
    </style>'''
    else:
        printer_style = ''

    if forceOWADesktop:
        # Outlook Web App does not evaluate media queries so upstream repeats
        # every rule prefixed with "[owa] " outside of any "@media" block.
        owa_str = '\n'.join(
            f'[owa] {media_query_str}'
            for media_query_str in media_queries_str.split('\n')
        )
        owa_style = f'<style type="text/css">\n{owa_str}\n</style>'
    else:
        owa_style = ''

    return f'''
    <style type="text/css">
      @media only screen and (min-width:{breakpoint}) {{
          {media_queries_str}
      }}
    </style>
    <style media="screen and (min-width:{breakpoint})">
        {thunderbird_media_queries_str}
    </style>
    {printer_style}
    {owa_style}
    '''
