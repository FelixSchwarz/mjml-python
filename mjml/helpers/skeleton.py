
import textwrap

from jinja2 import Template

from .fonts import buildFontsTags
from .media_queries import buildMediaQueriesTags
from .preview import buildPreview
from .py_utils import is_not_nil


__all__ = ['skeleton_str']

# js: skeleton(...)
def skeleton_str(*,
    inlineStyle,
    title='', content='', backgroundColor='', breakpoint='480px', lang=None,
    fonts=None, mediaQueries=None, forceOWADesktop=False,
    headStyle=None, componentsHeadStyle=(), style=(), headRaw=(),
    classes=None,
    preview = None,
    defaultAttributes=None
    ):

    apply_breakpoints = lambda values: tuple(map(lambda v: v(breakpoint), values))
    components_head_style_strs = apply_breakpoints(componentsHeadStyle)

    if headStyle:
        # upstream expected an "iterable" (functions) but uses JavaScript's
        # iteration protocol: iterating over an object ("dict") iterates over
        # values not keys like in Python.
        assert hasattr(headStyle, 'values')
        headStyle = tuple(headStyle.values())
    else:
        headStyle = ()
    def apply_breakpoints(values):
        def _add_breakpoint(v):
            return v(breakpoint)
        return tuple(map(_add_breakpoint, values))
    head_style_strs = apply_breakpoints(headStyle)
    extra_style = f'<style type="text/css">{"".join(style)}</style>' if style else ''

    tmpl_vars = {
        'title'          : title,
        'content'        : content,
        'langAttribute'  : f'lang="{lang}" ' if lang else '',
        'backgroundColor': f' style="background-color:{backgroundColor};"' if backgroundColor else '',

        'font_tags_str'  : buildFontsTags(content, inlineStyle, fonts=fonts),
        'media_queries_str'  : buildMediaQueriesTags(breakpoint, mediaQueries, forceOWADesktop),
        'components_head_style_str': '\n'.join(components_head_style_strs),
        'head_style_strs': '\n'.join(head_style_strs),
        'extra_style': extra_style,
        'headRaw_str': '\n'.join(filter(is_not_nil, headRaw or ())),
        'preview_str'    : buildPreview(preview),
    }

    skeleton_tmpl = Template(skeleton_tmpl_str)
    return skeleton_tmpl.render(tmpl_vars)


skeleton_tmpl_str_raw = '''\
    <!doctype html>
    <html {{ langAttribute }}xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
      <head>
        <title>
          {{ title }}
        </title>
        <!--[if !mso]><!-- -->
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <!--<![endif]-->
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style type="text/css">
          #outlook a { padding:0; }
          body { margin:0;padding:0;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%; }
          table, td { border-collapse:collapse;mso-table-lspace:0pt;mso-table-rspace:0pt; }
          img { border:0;height:auto;line-height:100%; outline:none;text-decoration:none;-ms-interpolation-mode:bicubic; }
          p { display:block;margin:13px 0; }
        </style>
        <!--[if mso]>
        <xml>
        <o:OfficeDocumentSettings>
          <o:AllowPNG/>
          <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
        </xml>
        <![endif]-->
        <!--[if lte mso 11]>
        <style type="text/css">
          .mj-outlook-group-fix { width:100% !important; }
        </style>
        <![endif]-->
        {{ font_tags_str }}
        {{ media_queries_str }}
        <style type="text/css">

        {{ components_head_style_str }}
        {{ head_style_strs }}
        </style>
        {{ extra_style }}
        {{ headRaw_str }}
      </head>
      <body{{ backgroundColor }}>
        {{ preview_str }}
        {{ content }}
      </body>
    </html>'''

skeleton_tmpl_str = textwrap.dedent(skeleton_tmpl_str_raw)

