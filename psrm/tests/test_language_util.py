import pytest
from psrm.utils.language_util import convert_to_danish


@pytest.mark.parametrize('s, expected', [
    ('&#198;', 'Æ'),
    ('&#248;', 'ø'),
    ('&#229;', 'å'),
    ('&#198;&#248;&#229;', 'Æøå')
])
def test_convert_to_danish(s, expected):
    assert convert_to_danish(s) == expected