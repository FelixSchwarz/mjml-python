

__all__ = []

def _components():
    from ..elements import (MjButton, MjText, MjSection, MjColumn, MjBody,
        MjGroup, MjImage, MjDivider, MjTable)
    from ..elements.head import (MjAttributes, MjHead, MjStyle, MjTitle)
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
        # --- head components ---
        'mj-attributes': MjAttributes,
        'mj-head': MjHead,
        'mj-title': MjTitle,
        'mj-style': MjStyle,
    }
    return components
