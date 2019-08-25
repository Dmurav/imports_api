from datetime import date
from pprint import pprint

import pytest
from django.db.models import F
from hamcrest import assert_that, has_entries, contains, empty, contains_inanyorder, has_properties

from imports.api.models import DataSet, Citizen, CitizenRelative
from imports.api.operations import (create_dataset, update_citizen, get_birthday_stats,
                                    get_birthday_stats2, )
from imports.api.serializers import CitizenSerializer

pytestmark = pytest.mark.django_db


class TestCreateDataSetOperation:
    @pytest.fixture
    def created_data_set_id(self, create_citizens_data):
        return create_dataset(citizens=create_citizens_data)

    @pytest.fixture()
    def citizens_created(self, created_data_set_id):
        return list(Citizen.objects.filter(data_set_id=created_data_set_id).order_by('citizen_id'))

    def test_data_set_created(self, created_data_set_id):
        assert DataSet.objects.filter(id=created_data_set_id).exists()

    def test_citizens_created(self, created_data_set_id, create_citizens_data, citizens_created):
        citizen_101 = Citizen.objects.get(citizen_id=101, data_set_id=created_data_set_id)
        citizen_102 = Citizen.objects.get(citizen_id=102, data_set_id=created_data_set_id)
        citizen_103 = Citizen.objects.get(citizen_id=103, data_set_id=created_data_set_id)

        citizen_relatives = list(
                CitizenRelative.objects.all().values_list('citizen_id', 'relative_id'))

        facts = {
            'citizens_count': len(citizens_created),
            'citizen_101_relatives': list(citizen_101.relatives.all()),
            'citizen_102_relatives': list(citizen_102.relatives.all()),
            'citizen_103_relatives': list(citizen_103.relatives.all()),
            'citizen_relatives': citizen_relatives,
        }

        assert_that(facts, has_entries({
            'citizens_count': len(create_citizens_data),
            'citizen_101_relatives': contains(citizen_102),
            'citizen_102_relatives': contains(citizen_101),
            'citizen_103_relatives': empty(),
            'citizen_relatives': contains_inanyorder(
                    (citizen_101.id, citizen_102.id),
                    (citizen_102.id, citizen_101.id),
            )
        }))


class TestUpdateCitizenOperation:
    @pytest.fixture()
    def citizens(self, data_set):
        CitizenRelative.objects.all().delete()
        return list(data_set.citizens.all())

    def test_update_one_citizen(self, citizen1):
        data = {
            'town': 'СПБ',
            'street': 'Новая',
            'building': 'some',
            'apartment': 100,
            'name': 'Дима',
            'birth_date': date(year=1986, month=6, day=14),
            'gender': 'make',
        }
        updated = update_citizen(data_set_id=citizen1.data_set_id,
                                 citizen_id=citizen1.citizen_id,
                                 citizen_data=data)
        assert_that(updated, has_properties(data))

    def test_update_relatives(self, citizens):
        citizen1, citizen2, citizen3 = citizens

        update_citizen(data_set_id=citizen1.data_set_id,
                       citizen_id=citizen1.citizen_id,
                       citizen_data={
                           'relatives': [citizen2.citizen_id, citizen3.citizen_id]
                       })

        assert_that({
            'citizen1': citizen1,
            'citizen2': citizen2,
            'citizen3': citizen3,
        }, has_entries({
            'citizen1': has_properties({
                'relatives_ids': contains_inanyorder(citizen2.citizen_id, citizen3.citizen_id)
            }),
            'citizen2': has_properties({'relatives_ids': contains_inanyorder(citizen1.citizen_id)}),
            'citizen3': has_properties({'relatives_ids': contains_inanyorder(citizen1.citizen_id)}),
        }))


@pytest.mark.parametrize('create_citizens_data', [[]])
def test_birthday_stats_for_empty_data_set(data_set, create_citizens_data):
    stats = get_birthday_stats2(data_set.id)
    assert_that(stats, has_entries({
        str(month): [] for month in range(1, 12 + 1)
    }))


class TestBirthdaysOperationCase1:
    @pytest.fixture()
    def base_citizen_data(self):
        return {
            'town': 'Москва',
            'street': 'Новая',
            'building': '16к2стр5',
            'apartment': 1,
            'name': 'Александр',
            'gender': 'male',
        }

    @pytest.fixture()
    def create_citizens_data(self, base_citizen_data):
        data = [
            {
                'citizen_id': 101,
                'birth_date': date(year=1990, month=1, day=12),
                'relatives': [102],
            },
            {
                'citizen_id': 102,
                'birth_date': date(year=1993, month=10, day=25),
                'relatives': [101],
            },
            {
                'citizen_id': 103,
                'birth_date': date(year=1988, month=6, day=11),
                'relatives': [],
            }
        ]
        return [{**el, **base_citizen_data} for el in data]

    @pytest.fixture()
    def expected_stats(self):
        return {
            '1': contains_inanyorder({'citizen_id': 102, 'presents': 1}),
            '2': [],
            '3': [],
            '4': [],
            '5': [],
            '6': [],
            '7': [],
            '8': [],
            '9': [],
            '10': contains_inanyorder({'citizen_id': 101, 'presents': 1}),
            '11': [],
            '12': []
        }

    def test_stats(self, data_set, expected_stats):
        stats = get_birthday_stats(data_set.id)
        assert_that(stats, expected_stats)


class TestBirthdaysOperationCase2:
    @pytest.fixture()
    def base_citizen_data(self):
        return {
            'town': 'Москва',
            'street': 'Новая',
            'building': '16к2стр5',
            'apartment': 1,
            'name': 'Александр',
            'gender': 'male',
        }

    @pytest.fixture()
    def create_citizens_data(self, base_citizen_data):
        data = [
            {
                'citizen_id': 10,
                'birth_date': date(year=1990, month=7, day=12),
                'relatives': [20, 60, 70, 80],
            },
            {
                'citizen_id': 20,
                'birth_date': date(year=1993, month=1, day=25),
                'relatives': [10, 40, 50],
            },
            {
                'citizen_id': 30,
                'birth_date': date(year=1988, month=10, day=11),
                'relatives': [],
            },
            {
                'citizen_id': 40,
                'birth_date': date(year=1988, month=12, day=11),
                'relatives': [20, 50, 60, 70],
            },
            {
                'citizen_id': 50,
                'birth_date': date(year=1988, month=6, day=11),
                'relatives': [20, 40],
            },
            {
                'citizen_id': 60,
                'birth_date': date(year=1988, month=6, day=11),
                'relatives': [10, 40],
            },
            {
                'citizen_id': 70,
                'birth_date': date(year=1988, month=7, day=11),
                'relatives': [10, 40],
            },
            {
                'citizen_id': 80,
                'birth_date': date(year=1988, month=7, day=11),
                'relatives': [10],
            },
            {
                'citizen_id': 90,
                'birth_date': date(year=1988, month=11, day=11),
                'relatives': [],
            },
            {
                'citizen_id': 100,
                'birth_date': date(year=1988, month=11, day=11),
                'relatives': [],
            },
        ]
        return [{**el, **base_citizen_data} for el in data]

    @pytest.fixture()
    def expected_stats(self):
        return {
            '1': contains_inanyorder(
                    {'citizen_id': 10, 'presents': 1},
                    {'citizen_id': 40, 'presents': 1},
                    {'citizen_id': 50, 'presents': 1},
            ),
            '2': [],
            '3': [],
            '4': [],
            '5': [],
            '6': contains_inanyorder(
                    {'citizen_id': 10, 'presents': 1},
                    {'citizen_id': 20, 'presents': 1},
                    {'citizen_id': 40, 'presents': 2},
            ),
            '7': contains_inanyorder(
                    {'citizen_id': 10, 'presents': 2},
                    {'citizen_id': 20, 'presents': 1},
                    {'citizen_id': 40, 'presents': 1},
                    {'citizen_id': 60, 'presents': 1},
                    {'citizen_id': 70, 'presents': 1},
                    {'citizen_id': 80, 'presents': 1},
            ),
            '8': [],
            '9': [],
            '10': [],
            '11': [],
            '12': contains_inanyorder(
                    {'citizen_id': 20, 'presents': 1},
                    {'citizen_id': 50, 'presents': 1},
                    {'citizen_id': 60, 'presents': 1},
                    {'citizen_id': 70, 'presents': 1},
            )
        }

    def test_stats(self, data_set, expected_stats, create_citizens_data):
        stats = get_birthday_stats2(data_set.id)
        assert_that(stats, has_entries(expected_stats))
