

__all__ = ['buildMediaQueriesTags']

def buildMediaQueriesTags(breakpoint, mediaQueries=None, forceOWADesktop=False):
    if not mediaQueries:
        return ''
    elif hasattr(mediaQueries, 'items'):
        # dict
        mediaQueries = tuple(mediaQueries.items())

    def mqStr(item):
        className, mediaQuery = item
        return f'.{className} {mediaQuery}'
    baseMediaQueries = tuple(map(mqStr, mediaQueries))
    media_queries_str = '\n'.join(baseMediaQueries)

    def tbMqStr(item):
        className, mediaQuery = item
        return f'.moz-text-html .{className} {mediaQuery}'
    thunderbirdMediaQueries = tuple(map(tbMqStr, mediaQueries))
    thunderbird_media_queries_str = '\n'.join(thunderbirdMediaQueries)

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
    {owa_style}
    '''
