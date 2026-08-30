import pytest

from mjml.elements.mj_table import MjTable


@pytest.mark.parametrize(
    ('cellspacing', 'expected'),
    [
        ('0', False),
        ('invalid', False),
        ('4', True),
    ],
)
def test_has_cellspacing(cellspacing, expected):
    table = MjTable(attributes={'cellspacing': cellspacing}, context={})

    assert table.hasCellspacing() is expected
