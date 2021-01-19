
from mjml.core import initComponent, Component


__all__ = ['HeadComponent']

class HeadComponent(Component):
    def handlerChildren(self):
        def handle_children(children):
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

        childrens = self.props.children
        return tuple(map(handle_children, childrens))

