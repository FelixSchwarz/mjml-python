

__all__ = ['initComponent']

def _components():
    from ..elements import MjText, MjSection, MjColumn, MjBody, MjImage, MjDivider
    components = {
        'mj-text': MjText,
        'mj-divider': MjDivider,
        'mj-image': MjImage,
        'mj-section': MjSection,
        'mj-column': MjColumn,
        'mj-body': MjBody,
    }
    return components

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

