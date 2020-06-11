

__all__ = []

def _components():
    from ..elements import (MjButton, MjText, MjSection, MjColumn, MjBody,
        MjImage, MjDivider)
    components = {
        'mj-button': MjButton,
        'mj-text': MjText,
        'mj-divider': MjDivider,
        'mj-image': MjImage,
        'mj-section': MjSection,
        'mj-column': MjColumn,
        'mj-body': MjBody,
    }
    return components
