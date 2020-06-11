

from .registry import _components

__all__ = ['initComponent']

def initComponent(initialDatas, name):
    components = _components()
    component_cls = components[name]
    if not component_cls:
        return None

    component = component_cls(**initialDatas)
    if getattr(component, 'headStyle', None):
        component.context['addHeadStyle'](name, component.headStyle)
    if getattr(component, 'componentHeadStyle', None):
        component.context['addComponentHeadSyle'](component.componentHeadStyle)
    return component

