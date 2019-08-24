import pytest

pytestmark = pytest.mark.django_db

from imports.api.models import DataSet


def test_hey():
    assert DataSet.objects.count() == 0
