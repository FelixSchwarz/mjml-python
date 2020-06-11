

__all__ = []

def _components():
    from ..elements import (MjButton, MjText, MjSection, MjColumn, MjBody,
        MjImage, MjDivider)
    from ..elements.head import (MjHead, MjStyle, MjTitle)
    components = {
        'mj-button': MjButton,
        'mj-text': MjText,
        'mj-divider': MjDivider,
        'mj-image': MjImage,
        'mj-section': MjSection,
        'mj-column': MjColumn,
        'mj-body': MjBody,
        'mj-head': MjHead,
        'mj-title': MjTitle,
        'mj-style': MjStyle,
    }
    return components
