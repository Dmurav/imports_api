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

    CitizenRelative.objects.create(citizen=created[0], relative=created[1])
    CitizenRelative.objects.create(citizen=created[1], relative=created[0])
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
