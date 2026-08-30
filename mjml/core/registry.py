from collections.abc import Sequence
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from mjml.core.api import Component


__all__ = ['components_for_invocation', 'core_components']


def core_components() -> dict[str, type["Component"]]:
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

    return _by_tag_name([
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


def components_for_invocation(
    custom_components: Optional[Sequence[type["Component"]]] = None,
) -> dict[str, type["Component"]]:
    """
    The components a single mjml_to_html() call may use.

    Every call gets its own mapping so custom components can not leak into
    later or concurrent calls.
    """
    components = core_components()
    if custom_components:
        components.update(_by_tag_name(custom_components))
    return components


def _by_tag_name(source: Sequence[type["Component"]]) -> dict[str, type["Component"]]:
    return {component.component_name: component for component in source}
