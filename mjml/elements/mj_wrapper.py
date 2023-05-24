
from ..helpers import suffixCssClasses
from . import MjSection


__all__ = ['MjWrapper']


class MjWrapper(MjSection):
    component_name = 'mj-wrapper'

    def renderWrappedChildren(self):
        children = self.props['children']
        containerWidth = self.context['containerWidth']

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
