from datetime import date
from pprint import pprint

import pytest
from django.db.models import F
from hamcrest import assert_that, has_entries, contains, empty, contains_inanyorder, has_properties

from imports.api.models import DataSet, Citizen, CitizenRelative
from imports.api.operations import create_dataset, update_citizen, get_birthday_stats

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


class TestBirthdaysOperation:
    @pytest.fixture()
    def create_citizens_data(self):
        data = [
            {
                'citizen_id': 101,
                'town': 'Москва',
                'street': 'Новая',
                'building': '16к2стр5',
                'apartment': 1,
                'name': 'Александр',
                'birth_date': date(year=1990, month=1, day=12),
                'gender': 'male',
                'relatives': [102],
            },
            {
                'citizen_id': 102,
                'town': 'Москва',
                'street': 'Льва Толстого',
                'building': '16к2стр5',
                'apartment': 1,
                'name': 'Иван',
                'birth_date': date(year=1993, month=10, day=25),
                'gender': 'male',
                'relatives': [101],
            },
            {
                'citizen_id': 103,
                'town': 'Москва',
                'street': 'Другая',
                'building': '16к2стр5',
                'apartment': 1,
                'name': 'Татьяна',
                'birth_date': date(year=1988, month=6, day=11),
                'gender': 'female',
                'relatives': [],
            }
        ]
        return data

    def test_stats(self, data_set):
        stats = get_birthday_stats(data_set.id)
        print(stats)

    @pytest.mark.parametrize('create_citizens_data', [[]])
    def test_empty_data_set(self, data_set, create_citizens_data):
        stats = get_birthday_stats(data_set.id)
        assert_that(stats, has_entries({
            str(month): [] for month in range(1, 12 + 1)
        }))
