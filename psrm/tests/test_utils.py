from datetime import datetime
import pytest

from psrm.utils import utils

@pytest.mark.parametrize('a, expected', [
    (0, True),
    (1, True),
    (-1, True),
    ("1", True),
    ("a", False),
    ("1.0", False),
    (True, True),
    (False, True)
])
def test_is_integer(a, expected):
    value = utils.is_integer(a)
    assert value == expected


def test_get_date():
    assert utils.get_date() == datetime.today().strftime('%d-%m-%Y')


@pytest.mark.parametrize('date, expected', [
    ('2020-01-01', datetime(2020, 1, 1, 0, 0)),
    ('1989/7/3', datetime(1989, 7, 3, 0, 0)),
    ('1-21-2001', datetime(2001, 1, 21, 0, 0)),
    ('21-1-2001', datetime(2001, 1, 21, 0, 0))
])
def test_convert_date_from_str_positive(date, expected):
    assert utils.convert_date_from_str(date) == expected


@pytest.mark.parametrize('date, error', [
    ('2020-21-21', ValueError),
    (42, TypeError),
    (int, TypeError)
])
def test_convert_date_from_str_negative(date, error):
    with pytest.raises(error):
        utils.convert_date_from_str(date)
