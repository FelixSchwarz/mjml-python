import typing as t

from mjml.core import Component, initComponent


__all__ = ['HeadComponent']


class HeadComponent(Component):
    # TODO typing: figure out proper type annotations
    def handlerChildren(self):
        def handle_children(children: t.Dict[str, t.Any]) -> t.Optional[str]:
            tagName = children['tagName']
            component = initComponent(
                name = tagName,
                context = self.getChildContext(),
                **children
            )
            if not component:
                # LATER: hook up with error reporting structure
                # (e.g. via "context"? - upstream uses console.error() here)
                print(f'No matching component for tag : {tagName}')
                return None

            if hasattr(component, 'handler'):
                component.handler()
            if hasattr(component, 'render'):
                return component.render()
            return None

        childrens = self.props.get("children")
        return tuple(map(handle_children, childrens))
