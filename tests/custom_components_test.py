
from unittest import TestCase

from htmlcompare import assert_same_html

from mjml import mjml_to_html
from mjml.elements import MjText
from mjml.testing_helpers import get_mjml_fp, load_expected_html


class MjTextCustom(MjText):
    component_name = 'mj-text-custom'

    def render(self):
        content = super().render()

        return f'<div>START CUSTOM WRAPPER</div>{content}<div>END CUSTOM WRAPPER</div>'

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


class CustomComponentsTest(TestCase):
    def test_custom_components(self):
        expected_html = load_expected_html('_custom')
        with get_mjml_fp('_custom') as mjml_fp:
            result_list = mjml_to_html(mjml_fp, custom_components=[MjTextCustom, MjTextOverride])

        assert not result_list.errors
        list_actual_html = result_list.html
        assert_same_html(expected_html, list_actual_html, verbose=True)
