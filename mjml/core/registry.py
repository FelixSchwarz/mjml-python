
from collections.abc import Sequence
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from mjml.core.api import Component


__all__ = ['components', 'register_components', 'register_core_components']

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


def register_components(source: Sequence[type["Component"]]):
    for component in source:
        components[component.component_name] = component
