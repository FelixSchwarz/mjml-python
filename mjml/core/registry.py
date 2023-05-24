

__all__ = ['components', 'register_components', 'register_core_components']

from typing import List, Type


components = {}

def register_core_components():
    from ..elements import (
        MjAccordion,
        MjAccordionElement,
        MjAccordionText,
        MjAccordionTitle,
        MjBody,
        MjButton,
        MjCarousel,
        MjCarouselImage,
        MjColumn,
        MjDivider,
        MjGroup,
        MjHero,
        MjImage,
        MjNavbar,
        MjNavbarLink,
        MjRaw,
        MjSection,
        MjSocial,
        MjSocialElement,
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
        MjHtmlAttributes,
        MjPreview,
        MjStyle,
        MjTitle,
    )

    register_components([
        MjAccordion,
        MjAccordionElement,
        MjAccordionText,
        MjAccordionTitle,
        MjButton,
        MjCarousel,
        MjCarouselImage,
        MjText,
        MjDivider,
        MjHero,
        MjImage,
        MjSection,
        MjColumn,
        MjBody,
        MjGroup,
        MjTable,
        MjRaw,
        MjNavbar,
        MjNavbarLink,
        MjSocial,
        MjSocialElement,
        MjSpacer,
        MjWrapper,
        # --- head components ---
        MjAttributes,
        MjFont,
        MjHead,
        MjHtmlAttributes,
        MjPreview,
        MjTitle,
        MjStyle,
        MjBreakpoint,
    ])

    return components


def register_components(source: List[Type]):
    for component in source:
        components[component.component_name] = component
