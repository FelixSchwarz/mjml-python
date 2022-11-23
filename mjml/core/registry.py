

__all__ = []

def _components():
    from ..elements import (MjButton, MjText, MjSection, MjColumn, MjBody,
        MjGroup, MjImage, MjNavbar, MjNavbarLink, MjDivider, MjSpacer, MjTable, MjRaw, MjWrapper)
    from ..elements.head import (MjAttributes, MjBreakpoint, MjFont, MjHead, MjPreview, MjStyle,
        MjTitle)
    components = {
        'mj-button': MjButton,
        'mj-text': MjText,
        'mj-divider': MjDivider,
        'mj-image': MjImage,
        'mj-section': MjSection,
        'mj-column': MjColumn,
        'mj-body': MjBody,
        'mj-group'  : MjGroup,
        'mj-table'  : MjTable,
        'mj-raw'  : MjRaw,
        'mj-navbar': MjNavbar,
        'mj-navbar-link': MjNavbarLink,
        'mj-spacer': MjSpacer,
        'mj-wrapper': MjWrapper,
        # --- head components ---
        'mj-attributes': MjAttributes,
        'mj-font': MjFont,
        'mj-head': MjHead,
        'mj-preview': MjPreview,
        'mj-title': MjTitle,
        'mj-style': MjStyle,
        'mj-breakpoint': MjBreakpoint,
    }
    return components
