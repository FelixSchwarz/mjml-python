
from mjml.core import ComponentCategory

from ..helpers import suffixCssClasses
from . import MjSection


__all__ = ['MjWrapper']


class MjWrapper(MjSection):
    component_name = 'mj-wrapper'
    # not section level although it derives from MjSection: a wrapper takes
    # sections but must not be nested inside another wrapper
    categories = frozenset()
    accepts = frozenset({ComponentCategory.SECTION_LEVEL, ComponentCategory.RAW})

    @classmethod
    def allowed_attrs(cls):
        return {
            **super().allowed_attrs(),
            'gap': 'unit(px)',
        }

    def renderWrappedChildren(self):
        children = self.props['children']
        containerWidth = self.context.get('containerWidth')

        def render_child(component):
            if component.isRawElement():
                return component.render()
            td_ie_attrs = component.html_attrs(
                align=component.get_attr('align', missing_ok=True),
                class_=suffixCssClasses(
                      component.get_attr('css-class'),
                      'outlook',
                    ),
                width=containerWidth,
            )
            return f'''
              <!--[if mso | IE]>
                <tr>
                  <td {td_ie_attrs}>
              <![endif]-->
                {component.render()}
              <!--[if mso | IE]>
                  </td>
                 </tr>
              <![endif]-->
            '''

        return self.renderChildren(children, renderer=render_child)
