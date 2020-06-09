

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

    owa_style_str = ''
    if forceOWADesktop:
        owaQueries = map(lambda mq: f'[owa] {mq}', baseMediaQueries)
        owa_queries_str = '\n'.join(owaQueries)
        owa_style_str = f'<style type="text/css">\n{owa_queries_str}\n</style>'

    return f'''
    <style type="text/css">
      @media only screen and (min-width:{breakpoint}) {{
          {media_queries_str}
      }}
    </style>
    {owa_style_str}
    '''

