import pytest
from rest_framework.test import APIRequestFactory, APIClient


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
