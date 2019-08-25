from datetime import date

import pytest

from imports.utils import calculate_age


@pytest.mark.parametrize(['current_date', 'birth_date', 'result'], [
    [date(year=2019, month=5, day=10), date(year=2019, month=5, day=10), 0],
    [date(year=2019, month=5, day=10), date(year=1990, month=5, day=10), 29],
    [date(year=2019, month=5, day=10), date(year=1990, month=7, day=1), 29],
    [date(year=2019, month=5, day=10), date(year=1990, month=1, day=20), 28],
    [date(year=2019, month=5, day=10), date(year=1990, month=5, day=9), 28],
])
def test_calculate_age(current_date, birth_date, result):
    assert calculate_age(current_date=current_date, birth_date=birth_date) == result
