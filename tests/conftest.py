from datetime import date

import pytest
from rest_framework.test import APIRequestFactory, APIClient

from imports.api.models import Citizen, DataSet, CitizenRelative


@pytest.fixture(scope='session')
def api_request_factory():
    return APIRequestFactory()


@pytest.fixture(scope='session')
def api_client():
    return APIClient()


@pytest.fixture()
def citizens():
    data = [
        {
            'citizen_id': 1,
            'town': 'Москва',
            'street': 'Льва Толстого',
            'building': '16к2стр5',
            'apartment': 1,
            'name': 'Иванов Иван Иванович',
            'birth_date': '29.05.1990',
            'gender': 'male',
            'relatives': [2],
        },
        {
            'citizen_id': 2,
            'town': 'Москва',
            'street': 'Льва Толстого',
            'building': '16к2стр5',
            'apartment': 1,
            'name': 'Иванов Иван Иванович',
            'birth_date': '12.05.1990',
            'gender': 'male',
            'relatives': [1],
        },
        {
            'citizen_id': 3,
            'town': 'Москва',
            'street': 'Льва Толстого',
            'building': '16к2стр5',
            'apartment': 1,
            'name': 'Татьяна',
            'birth_date': '16.05.1990',
            'gender': 'female',
            'relatives': [],
        }
    ]
    return data


@pytest.fixture()
def create_citizens_data():
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


@pytest.fixture()
def data_set(create_citizens_data):
    """Create data set of 3 citizens in DB."""
    ds = DataSet.objects.create()
    created = []
    for data in create_citizens_data:
        data = data.copy()
        data.pop('relatives')
        created.append(Citizen.objects.create(**data, data_set=ds))

    pairs = {}
    for citizen in create_citizens_data:
        citizen_id = citizen['citizen_id']
        relatives = set(citizen['relatives'])
        for relative_id in relatives:
            assert citizen_id not in relatives
            pair = (min(citizen_id, relative_id), max(citizen_id, relative_id))
            pairs[pair] = pairs.get(pair, 0) + 1

    for _, count in pairs.items():
        assert count == 2

    for citizen_id, relative_id in pairs.keys():
        citizen = Citizen.objects.get(citizen_id=citizen_id, data_set=ds)
        relative = Citizen.objects.get(citizen_id=relative_id, data_set=ds)
        CitizenRelative.objects.create(citizen=citizen, relative=relative)
        CitizenRelative.objects.create(citizen=relative, relative=citizen)

    return ds


@pytest.fixture()
def citizen1(data_set):
    return data_set.citizens.order_by('citizen_id')[0]


@pytest.fixture()
def citizen2(data_set):
    return data_set.citizens.order_by('citizen_id')[1]


@pytest.fixture()
def citizen3(data_set):
    return data_set.citizens.order_by('citizen_id')[2]
