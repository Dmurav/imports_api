import pytest
from hamcrest import assert_that, contains_inanyorder

from imports.api.models import CitizenRelative

pytestmark = pytest.mark.django_db


def test_birthdays_manager_method(data_set):
    data = CitizenRelative.objects.get_birthdays(data_set_id=data_set.id)

    expected_data = []
    for citizen in data_set.citizens.all().prefetch_related('relatives'):
        for relative in citizen.relatives.all():
            expected_data.append({
                'citizen_id': citizen.citizen_id,
                'relative_id': relative.citizen_id,
                'relative_birth_date': relative.birth_date,
            })

    expected_data = sorted(
            expected_data,
            key=lambda d: (d['citizen_id'], d['relative_id'], d['relative_birth_date'])
    )

    assert_that(data, contains_inanyorder(
            *expected_data,
    ))
