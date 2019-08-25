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
def data_set(citizens):
    """Create data set of 3 citizens in DB."""
    data_set = DataSet.objects.create()
    created = []
    for data in citizens:
        data = data.copy()
        data.pop('relatives')
        created.append(Citizen.objects.create(**data, data_set=data_set))

    CitizenRelative.objects.create(citizen=created[0], relative=created[1])
    CitizenRelative.objects.create(citizen=created[1], relative=created[0])
    return data_set
