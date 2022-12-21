

__all__ = []

components = {}

def _components():
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
