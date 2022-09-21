

__all__ = []

def _components():
    from ..elements import (MjButton, MjText, MjSection, MjColumn, MjBody,
        MjGroup, MjImage, MjDivider, MjSpacer, MjTable, MjRaw, MjWrapper)
    from ..elements.head import (MjAttributes, MjFont, MjHead, MjPreview, MjStyle,
        MjTitle)
    components = {
        'mj-body'      : MjBody,
        'mj-button'    : MjButton,
        'mj-column'    : MjColumn,
        'mj-divider'   : MjDivider,
        'mj-group'     : MjGroup,
        'mj-image'     : MjImage,
        'mj-raw'       : MjRaw,
        'mj-section'   : MjSection,
        'mj-spacer'    : MjSpacer,
        'mj-table'     : MjTable,
        'mj-text'      : MjText,
        'mj-wrapper'   : MjWrapper,
        # --- head components ---
        'mj-attributes': MjAttributes,
        'mj-font'      : MjFont,
        'mj-head'      : MjHead,
        'mj-preview'   : MjPreview,
        'mj-style'     : MjStyle,
        'mj-title'     : MjTitle,
    }
    return components
