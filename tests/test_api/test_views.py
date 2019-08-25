import pytest
from django.urls import reverse
from hamcrest import assert_that, has_entries, has_properties
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
    pass
