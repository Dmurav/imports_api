import pytest
from django.urls import reverse
from hamcrest import assert_that, has_entries, has_properties, contains_inanyorder
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def data_sets(mocker):
    data_sets = []

    def func(*args, **kwargs):
        from imports.api.operations import create_dataset
        data_set_id = create_dataset(*args, **kwargs)
        data_sets.append(data_set_id)
        return data_set_id

    mocker.patch('imports.api.views.create_dataset', func)
    return data_sets


class TestCreateDataSetView:
    @pytest.fixture
    def url(self):
        return reverse('create_dataset')

    def test_url(self, url):
        assert url == '/imports'

    def test_normal_request(self, api_client, citizens, data_sets, url):
        data = {
            'citizens': citizens,
        }
        response = api_client.post(url, data=data)
        assert_that(response, has_properties({
            'data': has_entries({
                'data': {
                    'import_id': data_sets[0]
                }
            }),
            'status_code': status.HTTP_201_CREATED,
        }))

    def test_empty_citizens_request(self, api_client):
        url = reverse('create_dataset')
        data = {
            'citizens': [],
        }
        response = api_client.post(url, data=data)
        assert_that(response, has_properties({
            'status_code': status.HTTP_400_BAD_REQUEST,
        }))

    def test_unknown_fields_request(self, api_client, citizens):
        citizens[0]['unknown'] = 'unknown'
        url = reverse('create_dataset')
        data = {
            'citizens': citizens,
        }
        response = api_client.post(url, data=data)
        assert_that(response, has_properties({
            'status_code': status.HTTP_400_BAD_REQUEST,
        }))


class TestUpdateCitizenView():
    @pytest.fixture()
    def url(self, citizen1):
        return reverse('update_citizen', kwargs={
            'data_set_id': citizen1.data_set_id,
            'citizen_id': citizen1.citizen_id,
        })

    def test_url(self, url, citizen1):
        assert url == f'/imports/{citizen1.data_set_id}/citizens/{citizen1.citizen_id}'

    def test_response_on_empty_data(self, api_client, url):
        request_data = {}
        response = api_client.patch(url, data=request_data)
        assert_that(response, has_properties({
            'status_code': status.HTTP_400_BAD_REQUEST,
        }))

    def test_response_on_correct_data(self, api_client, url, citizen1, data_set):
        request_data = {
            'town': 'СПБ',
            'street': 'Новая',
            'building': 'some',
            'apartment': 100,
            'name': 'Дима',
            'birth_date': '14.06.1986',
            'gender': 'male',
            'relatives': []
        }
        response = api_client.patch(url, data=request_data)

        citizen1.refresh_from_db()
        assert_that(response, has_properties({
            'status_code': status.HTTP_200_OK,
            'data': has_entries({
                'data': has_entries({
                    'citizen_id': citizen1.citizen_id,
                    'town': 'СПБ',
                    'street': 'Новая',
                    'building': 'some',
                    'apartment': 100,
                    'name': 'Дима',
                    'birth_date': '14.06.1986',
                    'gender': 'male',
                    'relatives': citizen1.relatives_ids,
                })
            })
        }))


class TestListsDataSetCitizensView:
    @pytest.fixture()
    def url(self, data_set):
        return reverse('list_citizens', kwargs={
            'data_set_id': data_set.id,
        })

    def test_url(self, url, data_set):
        assert url == f'/imports/{data_set.id}/citizens'

    def citizen_to_json(self, citizen):
        return {
            'citizen_id': citizen.citizen_id,
            'town': citizen.town,
            'street': citizen.street,
            'building': citizen.building,
            'apartment': citizen.apartment,
            'name': citizen.name,
            'birth_date': citizen.birth_date.strftime('%d.%m.%Y'),
            'gender': citizen.gender,
            'relatives': citizen.relatives_ids,
        }

    def test_response(self, api_client, url, data_set):
        response = api_client.get(url)

        assert_that(response, has_properties({
            'status_code': status.HTTP_200_OK,
            'data': has_entries({
                'data': contains_inanyorder(
                        *[self.citizen_to_json(citizen) for citizen in data_set.citizens.all()],
                )
            })
        }))


class TestBirthdaysView:
    @pytest.fixture()
    def url(self, data_set):
        return reverse('get_birthdays', kwargs={
            'data_set_id': data_set.id,
        })

    def test_url(self, url, data_set):
        assert url == f'/imports/{data_set.id}/citizens/birthdays'

    def test_response(self, api_client, url, data_set):
        response = api_client.get(url)
        assert_that(response, has_properties({
            'status_code': status.HTTP_200_OK,
            'data': has_entries({
                'data': has_entries({
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
                })
            })
        }))


class TestTownAgePercentilesView:
    @pytest.fixture()
    def url(self, data_set):
        return reverse('get_age_percentiles', kwargs={
            'data_set_id': data_set.id,
        })

    def test_url(self, url, data_set):
        assert url == f'/imports/{data_set.id}/towns/stat/percentile/age'

    def test_response(self, api_client, url, data_set):
        response = api_client.get(url)
        assert_that(response, has_properties({
            'status_code': status.HTTP_200_OK,
            'data': has_entries({
                'data': contains_inanyorder(
                    {'town': 'Москва', 'p50': 28.0, 'p75': 29.0, 'p99': 29.96}
                )
            }),
        }))
