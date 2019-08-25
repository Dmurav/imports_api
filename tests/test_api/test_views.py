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

    def test_response(self, api_client, url, data_set, citizen1, citizen2, citizen3):
        response = api_client.get(url)
        assert_that(response, has_properties({
            'status_code': status.HTTP_200_OK,
            'data': has_entries({
                'data': contains_inanyorder(
                        {
                            'citizen_id': citizen1.citizen_id,
                            'town': citizen1.town,
                            'street': citizen1.street,
                            'building': citizen1.building,
                            'apartment': citizen1.apartment,
                            'name': citizen1.name,
                            'birth_date': citizen1.birth_date.strftime('%d.%m.%Y'),
                            'gender': citizen1.gender,
                            'relatives': citizen1.relatives_ids,
                        },
                        {
                            'citizen_id': citizen2.citizen_id,
                            'town': citizen2.town,
                            'street': citizen2.street,
                            'building': citizen2.building,
                            'apartment': citizen2.apartment,
                            'name': citizen2.name,
                            'birth_date': citizen2.birth_date.strftime('%d.%m.%Y'),
                            'gender': citizen2.gender,
                            'relatives': citizen2.relatives_ids,
                        },
                        {
                            'citizen_id': citizen3.citizen_id,
                            'town': citizen3.town,
                            'street': citizen3.street,
                            'building': citizen3.building,
                            'apartment': citizen3.apartment,
                            'name': citizen3.name,
                            'birth_date': citizen3.birth_date.strftime('%d.%m.%Y'),
                            'gender': citizen3.gender,
                            'relatives': citizen3.relatives_ids,
                        },
                )
            })
        }))
