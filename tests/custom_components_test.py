
from io import StringIO

from htmlcompare import assert_same_html

from mjml import mjml_to_html
from mjml.core.registry import components_for_invocation
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


def test_custom_components():
    expected_html = load_expected_html('custom-component')
    with get_mjml_fp('custom-component') as mjml_fp:
        result_list = mjml_to_html(mjml_fp, custom_components=[MjTextCustom, MjTextOverride])

    assert not result_list.errors
    list_actual_html = result_list.html
    assert_same_html(expected_html, list_actual_html, verbose=True)


def test_custom_components_are_not_registered_globally():
    assert 'mj-text-custom' in components_for_invocation([MjTextCustom])
    assert 'mj-text-custom' not in components_for_invocation()


def test_custom_components_do_not_leak_into_later_calls():
    mjml = (
        '<mjml><mj-body><mj-section><mj-column>'
        '<mj-text-custom>text</mj-text-custom>'
        '</mj-column></mj-section></mj-body></mjml>'
    )
    html = mjml_to_html(StringIO(mjml), custom_components=[MjTextCustom]).html
    assert 'START CUSTOM WRAPPER' in html

    # the next call must not know "mj-text-custom" any more, so it is skipped
    assert 'START CUSTOM WRAPPER' not in mjml_to_html(StringIO(mjml)).html
