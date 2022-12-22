from mjml.elements import MjText

__all__ = ['MjTextOverride']


class MjTextOverride(MjText):
    @classmethod
    def default_attrs(cls):
        attrs = super().default_attrs()
        return {
            **attrs,
            'align'            : 'right',
            'color'            : 'red',
            'font-size'        : '26px',
        }

    def render(self):
        content = super().render()

        return f'<div>***</div>{content}<div>***</div>'
