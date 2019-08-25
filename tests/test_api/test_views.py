import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_create_dataset(api_client):
    print(api_client)

    url = reverse('create_dataset')
    response = api_client.post(url)
    response.render()
    print(response.content)
