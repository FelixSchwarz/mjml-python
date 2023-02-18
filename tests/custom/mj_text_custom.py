from mjml.elements import MjText

__all__ = ['MjTextCustom']


class MjTextCustom(MjText):
    component_name = 'mj-text-custom'

    def render(self):
        content = super().render()

        return f'<div>START CUSTOM WRAPPER</div>{content}<div>END CUSTOM WRAPPER</div>'
