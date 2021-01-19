

__all__ = []

def _components():
    from ..elements import (MjButton, MjText, MjSection, MjColumn, MjBody,
        MjGroup, MjImage, MjDivider, MjTable, MjRaw)
    from ..elements.head import (MjAttributes, MjFont, MjHead, MjPreview, MjStyle,
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
        # --- head components ---
        'mj-attributes': MjAttributes,
        'mj-font': MjFont,
        'mj-head': MjHead,
        'mj-preview': MjPreview,
        'mj-title': MjTitle,
        'mj-style': MjStyle,
    }
    return components
