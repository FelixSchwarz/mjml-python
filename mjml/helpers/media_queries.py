

__all__ = ['buildMediaQueriesTags']

def buildMediaQueriesTags(breakpoint, mediaQueries=None):
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

    return f'''
    <style type="text/css">
      @media only screen and (min-width:{breakpoint}) {{
          {media_queries_str}
      }}
    </style>
    <style media="screen and (min-width:{breakpoint})">
        {thunderbird_media_queries_str}
    </style>
    '''

