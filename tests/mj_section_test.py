import pytest

from mjml.core.types import initialize_type
from mjml.elements.mj_section import MjSection


def test_is_full_width():
    section = MjSection(attributes={'full-width': 'full-width'}, context={})

    assert section.isFullWidth() is True


@pytest.mark.parametrize('value', [False, '', 'nonsense'])
def test_is_not_full_width(value):
    section = MjSection(attributes={'full-width': value}, context={})

    assert section.isFullWidth() is False


def test_full_width_accepts_the_values_which_disable_it():
    full_width = initialize_type(MjSection.allowed_attrs()['full-width'])

    assert full_width.is_valid('full-width')
    # 'full-width="false"' is converted to a boolean before validation
    assert full_width.is_valid(False)
    assert full_width.is_valid('')
    assert not full_width.is_valid(True)
