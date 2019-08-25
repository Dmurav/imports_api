import pytest
from rest_framework.test import APIRequestFactory, APIClient


@pytest.fixture(scope='session')
def api_request_factory():
    return APIRequestFactory()


@pytest.fixture(scope='session')
def api_client():
    return APIClient()
