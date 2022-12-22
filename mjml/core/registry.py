

__all__ = ['assign_components', 'components', 'handle_mjml_config_components', 'preset_core_components', 'register_component']

import inspect
from types import ModuleType
from typing import Type

components = {}

def preset_core_components():
    from ..elements import (MjButton, MjText, MjSection, MjColumn, MjBody,
        MjGroup, MjImage, MjNavbar, MjNavbarLink, MjDivider, MjSpacer, MjTable, MjRaw, MjWrapper)
    from ..elements.head import (MjAttributes, MjBreakpoint, MjFont, MjHead, MjPreview, MjStyle,
        MjTitle)

    assign_components(components, [
        MjButton,
        MjText,
        MjDivider,
        MjImage,
        MjSection,
        MjColumn,
        MjBody,
        MjGroup,
        MjTable,
        MjRaw,
        MjNavbar,
        MjNavbarLink,
        MjSpacer,
        MjWrapper,
        # --- head components ---
        MjAttributes,
        MjFont,
        MjHead,
        MjPreview,
        MjTitle,
        MjStyle,
        MjBreakpoint,
    ])

    return components

def assign_components(target, source):
    for component in source:
        target[component.component_name] = component


def register_component(Component: Type):
    assign_components(components, [Component])


def register_custom_component(
    comp,
    registerCompFn=register_component,
):
    try:
        registerCompFn(comp)
    except AttributeError:
        if isinstance(comp, ModuleType):
            # Convert module into list of submodules
            comp = list([cls for name, cls in inspect.getmembers(comp) if inspect.isclass(cls)])

        for component in comp:
            register_custom_component(component, registerCompFn)


def handle_mjml_config_components(components):
    register_custom_component(components)
