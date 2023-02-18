

__all__ = ['components', 'register_components', 'register_core_components']

from typing import List, Type


components = {}

def register_core_components():
    from ..elements import (
        MjBody,
        MjButton,
        MjColumn,
        MjDivider,
        MjGroup,
        MjImage,
        MjNavbar,
        MjNavbarLink,
        MjRaw,
        MjSection,
        MjSpacer,
        MjTable,
        MjText,
        MjWrapper,
    )
    from ..elements.head import (
        MjAttributes,
        MjBreakpoint,
        MjFont,
        MjHead,
        MjPreview,
        MjStyle,
        MjTitle,
    )

    register_components([
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


def register_components(source: List[Type]):
    for component in source:
        components[component.component_name] = component
